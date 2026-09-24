import os
import uuid
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import ScopeChecker
from app.core.exceptions import (
    EntityAlreadyExistsException,
    EntityNotFoundException,
    ForbiddenException,
    ValidationException,
)
from app.core.logging import get_logger
from app.core.storage import (
    compute_sha256,
    get_storage_provider,
    validate_file_magic_bytes,
)
from app.models.field import (
    FieldAssignment,
    FieldDocument,
    FieldPhoto,
    FieldSurveyRecord,
)
from app.models.parcel import LandParcel
from app.models.user import User
from app.repositories.audit import AuditRepository
from app.repositories.field import FieldRepository
from app.repositories.parcel import ParcelRepository
from app.repositories.project import ProjectRepository
from app.repositories.user import UserRepository
from app.schemas.field import (
    EvidenceVerificationRequest,
    FieldAssignmentCreate,
    FieldAssignmentRead,
    FieldDocumentRead,
    FieldPhotoRead,
    FieldSurveyCreate,
    FieldSurveyRead,
)

logger = get_logger(__name__)


class FieldService:
    """Service orchestrating field officer assignments, ground surveys, and evidence uploads."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.field_repo = FieldRepository(session)
        self.parcel_repo = ParcelRepository(session)
        self.project_repo = ProjectRepository(session)
        self.user_repo = UserRepository(session)
        self.audit_repo = AuditRepository(session)
        self.storage = get_storage_provider()

    # -------------------------------------------------------------------------
    # Field Assignments
    # -------------------------------------------------------------------------

    async def create_assignment(
        self,
        assignment_in: FieldAssignmentCreate,
        current_user: User,
    ) -> FieldAssignmentRead:
        """Assign land parcel to a field officer for ground verification."""
        parcel = await self.parcel_repo.get_by_id(assignment_in.parcel_id)
        if not parcel:
            raise EntityNotFoundException("LandParcel", assignment_in.parcel_id)

        # Check geographic scope (District officer / Admin)
        ScopeChecker.verify_parcel_access(current_user, parcel)

        # Verify assigned officer exists and has FIELD_OFFICER role
        officer = await self.user_repo.get_by_id(assignment_in.assigned_officer_id)
        if not officer:
            raise EntityNotFoundException("User", assignment_in.assigned_officer_id)

        if "FIELD_OFFICER" not in officer.role_names and "ADMIN" not in officer.role_names:
            raise ValidationException(
                f"User '{officer.username}' does not hold the 'FIELD_OFFICER' role."
            )

        # Generate assignment ID
        assignment_id = assignment_in.id or f"ASN-{date.today().year}-{uuid.uuid4().hex[:6].upper()}"

        assignment = FieldAssignment(
            id=assignment_id,
            parcel_id=parcel.id,
            project_id=parcel.project_id,
            assigned_officer_id=officer.id,
            assigned_by_id=current_user.id,
            assigned_date=date.today(),
            due_date=assignment_in.due_date,
            priority=assignment_in.priority,
            status="Pending",
            required_tasks=assignment_in.required_tasks or [],
            remarks=assignment_in.remarks,
        )

        # Bind parcel to assigned officer
        parcel.assigned_officer_id = officer.id
        self.session.add(parcel)

        created = await self.field_repo.create_assignment(assignment)

        # Audit & Notification
        await self.audit_repo.log_action(
            user_id=current_user.id,
            user_name=current_user.full_name,
            role=current_user.role_names[0] if current_user.role_names else "OFFICER",
            action="FIELD_ASSIGNMENT_CREATED",
            module="field",
            entity_type="FieldAssignment",
            entity_id=created.id,
            details=f"Assigned parcel '{parcel.id}' to officer '{officer.full_name}'. Priority: {created.priority}",
        )

        await self.audit_repo.create_notification(
            title=f"New Field Assignment: {parcel.survey_number}",
            message=f"You have been assigned parcel '{parcel.id}' in {parcel.village}, {parcel.district}.",
            category="field",
            recipient_role="FIELD_OFFICER",
            user_id=officer.id,
            link_view="field_upload",
        )

        logger.info(f"Assignment '{created.id}' created for officer '{officer.username}'.")
        return self._to_assignment_read(created, parcel, officer)

    async def list_assignments(
        self,
        *,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        project_id: Optional[str] = None,
        parcel_id: Optional[str] = None,
        current_user: User,
        skip: int = 0,
        limit: int = 50,
    ) -> List[FieldAssignmentRead]:
        """List assignments subject to user role and geographic scope."""
        user_roles = set(r.upper() for r in current_user.role_names)

        assigned_officer_id = None
        allowed_states = None
        allowed_districts = None

        if "FIELD_OFFICER" in user_roles and "ADMIN" not in user_roles:
            assigned_officer_id = current_user.id
        elif "DISTRICT_OFFICER" in user_roles and "ADMIN" not in user_roles:
            allowed_states = [current_user.state] if current_user.state else None
            allowed_districts = [current_user.district] if current_user.district else None
        elif "STATE_OFFICIAL" in user_roles and "ADMIN" not in user_roles:
            allowed_states = [current_user.state] if current_user.state else None

        assignments = await self.field_repo.list_assignments(
            assigned_officer_id=assigned_officer_id,
            status=status,
            priority=priority,
            project_id=project_id,
            parcel_id=parcel_id,
            allowed_states=allowed_states,
            allowed_districts=allowed_districts,
            skip=skip,
            limit=limit,
        )

        result = []
        for a in assignments:
            result.append(self._to_assignment_read(a, a.parcel, a.assigned_officer))
        return result

    async def update_assignment_status(
        self,
        assignment_id: str,
        new_status: str,
        remarks: Optional[str],
        current_user: User,
    ) -> FieldAssignmentRead:
        """Update field assignment status."""
        assignment = await self.field_repo.get_assignment_by_id(assignment_id)
        if not assignment:
            raise EntityNotFoundException("FieldAssignment", assignment_id)

        user_roles = set(r.upper() for r in current_user.role_names)
        if "FIELD_OFFICER" in user_roles and "ADMIN" not in user_roles:
            if assignment.assigned_officer_id != current_user.id:
                raise ForbiddenException("You can only update your own assigned tasks.")

        assignment.status = new_status
        if remarks:
            assignment.remarks = f"{assignment.remarks or ''} | {remarks}".strip(" |")

        self.session.add(assignment)
        await self.session.flush()

        await self.audit_repo.log_action(
            user_id=current_user.id,
            user_name=current_user.full_name,
            role=current_user.role_names[0] if current_user.role_names else "OFFICER",
            action="FIELD_ASSIGNMENT_STATUS_UPDATED",
            module="field",
            entity_type="FieldAssignment",
            entity_id=assignment.id,
            details=f"Updated status to '{new_status}'. Remarks: {remarks or 'None'}",
        )

        return self._to_assignment_read(assignment, assignment.parcel, assignment.assigned_officer)

    # -------------------------------------------------------------------------
    # Field Survey Enumeration
    # -------------------------------------------------------------------------

    async def create_survey_record(
        self,
        survey_in: FieldSurveyCreate,
        current_user: User,
    ) -> FieldSurveyRead:
        """Create structured ground inspection survey record."""
        parcel = await self.parcel_repo.get_by_id(survey_in.parcel_id)
        if not parcel:
            raise EntityNotFoundException("LandParcel", survey_in.parcel_id)

        # Verify field officer assignment
        self._verify_field_officer_assignment(current_user, parcel)

        survey_id = survey_in.id or f"SRV-{date.today().year}-{uuid.uuid4().hex[:6].upper()}"

        survey_record = FieldSurveyRecord(
            id=survey_id,
            assignment_id=survey_in.assignment_id,
            parcel_id=parcel.id,
            project_id=parcel.project_id,
            officer_id=current_user.id,
            survey_date=date.today(),
            survey_type=survey_in.survey_type,
            structures_observed=survey_in.structures_observed,
            crops_observed=survey_in.crops_observed,
            trees_count=survey_in.trees_count,
            wells_count=survey_in.wells_count,
            remarks=survey_in.remarks,
            verification_status="Pending",
        )

        created = await self.field_repo.create_survey_record(survey_record)

        await self.audit_repo.log_action(
            user_id=current_user.id,
            user_name=current_user.full_name,
            role=current_user.role_names[0] if current_user.role_names else "FIELD_OFFICER",
            action="FIELD_SURVEY_SUBMITTED",
            module="field",
            entity_type="FieldSurveyRecord",
            entity_id=created.id,
            details=f"Survey submitted for parcel '{parcel.id}'. Trees: {created.trees_count}, Wells: {created.wells_count}",
        )

        return FieldSurveyRead(
            id=created.id,
            parcel_id=created.parcel_id,
            project_id=created.project_id,
            assignment_id=created.assignment_id,
            officer_id=created.officer_id,
            officer_name=current_user.full_name,
            survey_date=created.survey_date,
            survey_type=created.survey_type,
            structures_observed=created.structures_observed,
            crops_observed=created.crops_observed,
            trees_count=created.trees_count,
            wells_count=created.wells_count,
            remarks=created.remarks,
            verification_status=created.verification_status,
            created_at=created.created_at,
        )

    # -------------------------------------------------------------------------
    # Geotagged Photo Upload
    # -------------------------------------------------------------------------

    async def upload_field_photo(
        self,
        *,
        file_bytes: bytes,
        filename: str,
        parcel_id: str,
        assignment_id: Optional[str] = None,
        photo_type: str = "Boundary Marker",
        caption: str,
        latitude: float,
        longitude: float,
        accuracy_meters: float,
        captured_at: Optional[datetime] = None,
        current_user: User,
    ) -> FieldPhotoRead:
        """Validate magic bytes, compute SHA-256, store in object storage, and persist photo record."""
        # 1. Validate real image content (magic bytes)
        detected_mime = validate_file_magic_bytes(file_bytes, filename)
        if not detected_mime.startswith("image/"):
            raise ValidationException(f"Invalid file type '{detected_mime}'. Expected image file.")

        # 2. Verify target parcel and assignment permissions
        parcel = await self.parcel_repo.get_by_id(parcel_id)
        if not parcel:
            raise EntityNotFoundException("LandParcel", parcel_id)

        self._verify_field_officer_assignment(current_user, parcel)

        # 3. Calculate SHA-256 hash
        file_hash = compute_sha256(file_bytes)

        # 4. Save to object storage
        storage_key, photo_url = await self.storage.upload_file(
            file_bytes=file_bytes,
            filename=filename,
            content_type=detected_mime,
            directory=f"photos/{parcel_id}",
        )

        photo_id = f"PH-{uuid.uuid4().hex[:8].upper()}"

        photo = FieldPhoto(
            id=photo_id,
            parcel_id=parcel_id,
            assignment_id=assignment_id,
            uploader_id=current_user.id,
            officer_name=current_user.full_name,
            caption=caption,
            photo_type=photo_type,
            storage_key=storage_key,
            filename=filename,
            file_size_bytes=len(file_bytes),
            mime_type=detected_mime,
            document_hash=file_hash,
            photo_url=photo_url,
            thumbnail_url=photo_url,
            latitude=latitude,
            longitude=longitude,
            accuracy_meters=accuracy_meters,
            captured_at=captured_at or datetime.now(timezone.utc),
            status="Pending",
        )

        created = await self.field_repo.create_photo(photo)

        await self.audit_repo.log_action(
            user_id=current_user.id,
            user_name=current_user.full_name,
            role=current_user.role_names[0] if current_user.role_names else "FIELD_OFFICER",
            action="FIELD_PHOTO_UPLOADED",
            module="field",
            entity_type="FieldPhoto",
            entity_id=created.id,
            details=f"Geotagged photo uploaded for parcel '{parcel_id}' at GPS [{latitude}, {longitude}] (RTK Acc: {accuracy_meters}m). Hash: {file_hash[:16]}...",
        )

        return self._to_photo_read(created)

    # -------------------------------------------------------------------------
    # Field Document Upload
    # -------------------------------------------------------------------------

    async def upload_field_document(
        self,
        *,
        file_bytes: bytes,
        filename: str,
        parcel_id: str,
        assignment_id: Optional[str] = None,
        title: str,
        category: str = "Land Survey Report",
        current_user: User,
    ) -> FieldDocumentRead:
        """Validate, hash, store, and record legal/survey document."""
        # Validate magic bytes (PDF or image)
        detected_mime = validate_file_magic_bytes(file_bytes, filename)

        parcel = await self.parcel_repo.get_by_id(parcel_id)
        if not parcel:
            raise EntityNotFoundException("LandParcel", parcel_id)

        self._verify_field_officer_assignment(current_user, parcel)

        file_hash = compute_sha256(file_bytes)

        storage_key, file_url = await self.storage.upload_file(
            file_bytes=file_bytes,
            filename=filename,
            content_type=detected_mime,
            directory=f"documents/{parcel_id}",
        )

        doc_id = f"DOC-{uuid.uuid4().hex[:8].upper()}"

        doc = FieldDocument(
            id=doc_id,
            parcel_id=parcel_id,
            assignment_id=assignment_id,
            uploader_id=current_user.id,
            uploaded_by=current_user.full_name,
            title=title,
            category=category,
            storage_key=storage_key,
            filename=filename,
            file_size_bytes=len(file_bytes),
            mime_type=detected_mime,
            document_hash=file_hash,
            file_url=file_url,
            version="v1.0",
            status="Pending",
        )

        created = await self.field_repo.create_document(doc)

        await self.audit_repo.log_action(
            user_id=current_user.id,
            user_name=current_user.full_name,
            role=current_user.role_names[0] if current_user.role_names else "OFFICER",
            action="FIELD_DOCUMENT_UPLOADED",
            module="field",
            entity_type="FieldDocument",
            entity_id=created.id,
            details=f"Document '{title}' ({category}) uploaded for parcel '{parcel_id}'. Hash: {file_hash[:16]}...",
        )

        return self._to_doc_read(created)

    # -------------------------------------------------------------------------
    # Supervisory Verification / Rejection
    # -------------------------------------------------------------------------

    async def verify_evidence(
        self,
        *,
        evidence_type: str,  # photo or document
        evidence_id: str,
        verification_in: EvidenceVerificationRequest,
        current_user: User,
    ) -> Dict[str, Any]:
        """Supervisory approval or rejection of field photos or documents."""
        # Require supervisory role
        user_roles = set(r.upper() for r in current_user.role_names)
        if not bool(user_roles & {"DISTRICT_OFFICER", "STATE_OFFICIAL", "CENTRAL_OFFICIAL", "ADMIN"}):
            raise ForbiddenException("Only District Officers or higher supervisors can verify evidence.")

        if verification_in.status == "Rejected" and not verification_in.remarks:
            raise ValidationException("Mandatory remarks are required when rejecting evidence.")

        if evidence_type.lower() == "photo":
            photo = await self.field_repo.get_photo_by_id(evidence_id)
            if not photo:
                raise EntityNotFoundException("FieldPhoto", evidence_id)

            photo.status = verification_in.status
            photo.verified_by_id = current_user.id
            photo.verification_remarks = verification_in.remarks
            self.session.add(photo)
            target_parcel_id = photo.parcel_id
        elif evidence_type.lower() == "document":
            doc = await self.field_repo.get_document_by_id(evidence_id)
            if not doc:
                raise EntityNotFoundException("FieldDocument", evidence_id)

            doc.status = verification_in.status
            doc.verified_by_id = current_user.id
            doc.verification_remarks = verification_in.remarks
            self.session.add(doc)
            target_parcel_id = doc.parcel_id
        else:
            raise ValidationException(f"Invalid evidence type '{evidence_type}'. Must be 'photo' or 'document'.")

        await self.session.flush()

        await self.audit_repo.log_action(
            user_id=current_user.id,
            user_name=current_user.full_name,
            role=current_user.role_names[0] if current_user.role_names else "SUPERVISOR",
            action=f"EVIDENCE_{verification_in.status.upper()}",
            module="field",
            entity_type=evidence_type.title(),
            entity_id=evidence_id,
            details=f"Evidence {evidence_id} marked as {verification_in.status}. Remarks: {verification_in.remarks or 'N/A'}",
        )

        return {
            "status": "success",
            "evidence_type": evidence_type,
            "evidence_id": evidence_id,
            "verification_status": verification_in.status,
            "remarks": verification_in.remarks,
            "verified_by": current_user.full_name,
        }

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    def _verify_field_officer_assignment(self, user: User, parcel: LandParcel) -> None:
        """Enforce that a Field Officer can only operate on parcels assigned to them."""
        user_roles = set(r.upper() for r in user.role_names)
        if "ADMIN" in user_roles or "CENTRAL_OFFICIAL" in user_roles or "DISTRICT_OFFICER" in user_roles:
            return

        if "FIELD_OFFICER" in user_roles:
            if parcel.assigned_officer_id != user.id:
                raise ForbiddenException(
                    f"Access denied. Parcel '{parcel.id}' is not assigned to officer '{user.username}'."
                )

    @staticmethod
    def _to_assignment_read(
        assignment: FieldAssignment,
        parcel: Optional[LandParcel],
        officer: Optional[User],
    ) -> FieldAssignmentRead:
        return FieldAssignmentRead(
            id=assignment.id,
            parcel_id=assignment.parcel_id,
            project_id=assignment.project_id,
            assigned_officer_id=assignment.assigned_officer_id,
            assigned_officer_name=officer.full_name if officer else None,
            assigned_by_id=assignment.assigned_by_id,
            assigned_date=assignment.assigned_date,
            due_date=assignment.due_date,
            priority=assignment.priority,
            status=assignment.status,
            required_tasks=assignment.required_tasks or [],
            remarks=assignment.remarks,
            survey_number=parcel.survey_number if parcel else None,
            landowner_name=parcel.landowner_name if parcel else None,
            village=parcel.village if parcel else None,
            district=parcel.district if parcel else None,
            created_at=assignment.created_at,
            updated_at=assignment.updated_at,
        )

    @staticmethod
    def _to_photo_read(photo: FieldPhoto) -> FieldPhotoRead:
        return FieldPhotoRead(
            id=photo.id,
            parcel_id=photo.parcel_id,
            assignment_id=photo.assignment_id,
            officer_name=photo.officer_name,
            caption=photo.caption,
            photo_type=photo.photo_type,
            filename=photo.filename,
            file_size_bytes=photo.file_size_bytes,
            mime_type=photo.mime_type,
            document_hash=photo.document_hash,
            photo_url=photo.photo_url,
            thumbnail_url=photo.thumbnail_url,
            latitude=photo.latitude,
            longitude=photo.longitude,
            accuracy_meters=photo.accuracy_meters,
            captured_at=photo.captured_at,
            status=photo.status,
            verified_by_id=photo.verified_by_id,
            verification_remarks=photo.verification_remarks,
            created_at=photo.created_at,
        )

    @staticmethod
    def _to_doc_read(doc: FieldDocument) -> FieldDocumentRead:
        return FieldDocumentRead(
            id=doc.id,
            parcel_id=doc.parcel_id,
            assignment_id=doc.assignment_id,
            uploaded_by=doc.uploaded_by,
            title=doc.title,
            category=doc.category,
            filename=doc.filename,
            file_size_bytes=doc.file_size_bytes,
            mime_type=doc.mime_type,
            document_hash=doc.document_hash,
            file_url=doc.file_url,
            version=doc.version,
            status=doc.status,
            verified_by_id=doc.verified_by_id,
            verification_remarks=doc.verification_remarks,
            created_at=doc.created_at,
        )

