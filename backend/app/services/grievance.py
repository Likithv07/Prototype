import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import ScopeChecker
from app.core.exceptions import (
    EntityNotFoundException,
    ForbiddenException,
    ValidationException,
)
from app.core.logging import get_logger
from app.models.grievance import (
    Grievance,
    GrievanceDocument,
    GrievanceHistory,
)
from app.models.user import User
from app.repositories.audit import AuditRepository
from app.repositories.grievance import GrievanceRepository
from app.repositories.parcel import ParcelRepository
from app.repositories.user import UserRepository
from app.schemas.grievance import (
    GrievanceAssignRequest,
    GrievanceCreate,
    GrievanceDocumentRead,
    GrievanceFilter,
    GrievanceHistoryRead,
    GrievanceRead,
    GrievanceResolutionRequest,
    GrievanceStatusUpdateRequest,
)

logger = get_logger(__name__)


VALID_GRIEVANCE_TRANSITIONS = {
    "SUBMITTED": ["OFFICER_ASSIGNED", "REJECTED"],
    "OFFICER_ASSIGNED": ["UNDER_REVIEW", "REJECTED"],
    "UNDER_REVIEW": ["RESOLVED", "REJECTED"],
    "RESOLVED": [],
    "REJECTED": [],
}


class GrievanceService:
    """Domain service managing statutory grievance petitions, assignments, resolutions, and audit history."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.grievance_repo = GrievanceRepository(session)
        self.parcel_repo = ParcelRepository(session)
        self.user_repo = UserRepository(session)
        self.audit_repo = AuditRepository(session)

    def _verify_access(self, current_user: User, grievance: Grievance) -> None:
        """Enforce strict multi-tier scoping: citizens only access their own petitions; officers scoped to jurisdiction."""
        roles = set(r.upper() for r in current_user.role_names)

        # Central and Admin have national jurisdiction
        if "ADMIN" in roles or "CENTRAL_OFFICIAL" in roles:
            return

        # Citizen isolation
        if "CITIZEN" in roles:
            is_creator = (grievance.citizen_user_id == current_user.id)
            is_owner = (grievance.parcel and grievance.parcel.owner_user_id == current_user.id)
            if not (is_creator or is_owner):
                raise ForbiddenException("Access denied: Citizens may only view their own registered grievances.")
            return

        # Officer geographic scope
        if grievance.parcel:
            ScopeChecker.verify_parcel_access(current_user, grievance.parcel)
        else:
            raise ForbiddenException("Access denied: Unable to verify jurisdictional authority.")

    def _to_read_schema(self, g: Grievance) -> GrievanceRead:
        """Map SQLAlchemy Grievance to Pydantic GrievanceRead."""
        docs_read = [
            GrievanceDocumentRead(
                id=d.id,
                grievance_id=d.grievance_id,
                document_name=d.document_name,
                file_size_bytes=d.file_size_bytes,
                mime_type=d.mime_type,
                sha256_hash=d.sha256_hash,
                uploaded_by_name=d.uploaded_by_name,
                uploaded_at=d.uploaded_at,
            )
            for d in (g.documents or [])
        ]
        history_read = [
            GrievanceHistoryRead(
                id=h.id,
                grievance_id=h.grievance_id,
                action=h.action,
                from_status=h.from_status,
                to_status=h.to_status,
                performed_by_id=h.performed_by_id,
                performed_by_name=h.performed_by_name,
                performed_by_role=h.performed_by_role,
                notes=h.notes,
                created_at=h.created_at,
            )
            for h in (g.history or [])
        ]

        return GrievanceRead(
            id=g.id,
            parcel_id=g.parcel_id,
            project_id=g.project_id,
            citizen_user_id=g.citizen_user_id,
            citizen_name=g.citizen_name,
            citizen_phone=g.citizen_phone,
            category=g.category,
            subject=g.subject,
            description=g.description,
            status=g.status,
            priority=g.priority,
            assigned_officer_id=g.assigned_officer_id,
            assigned_officer_name=g.assigned_officer_name,
            assigned_date=g.assigned_date,
            resolution_notes=g.resolution_notes,
            resolved_by_name=g.resolved_by_name,
            resolved_at=g.resolved_at,
            sla_due_date=g.sla_due_date,
            created_at=g.created_at or datetime.now(timezone.utc),
            updated_at=g.updated_at or datetime.now(timezone.utc),
            documents=docs_read,
            history=history_read,
        )

    # -------------------------------------------------------------------------
    # 1. Grievance Creation & Retrieval
    # -------------------------------------------------------------------------

    async def create_grievance(
        self,
        payload: GrievanceCreate,
        current_user: User,
    ) -> GrievanceRead:
        """Lodge a statutory grievance petition with ownership validation and initial audit entry."""
        parcel = await self.parcel_repo.get_by_id(payload.parcel_id)
        if not parcel:
            raise EntityNotFoundException("LandParcel", payload.parcel_id)

        # Enforce that citizens can only file grievances on parcels they are authorized to access
        ScopeChecker.verify_parcel_access(current_user, parcel)

        now = datetime.now(timezone.utc)
        short_uuid = uuid.uuid4().hex[:6].upper()
        state_code = parcel.state[:2].upper() if parcel.state else "IN"
        grievance_id = f"GRV-2026-{state_code}-{short_uuid}"

        grievance = Grievance(
            id=grievance_id,
            parcel_id=parcel.id,
            project_id=parcel.project_id,
            citizen_user_id=current_user.id if "CITIZEN" in current_user.role_names else parcel.owner_user_id,
            citizen_name=payload.citizen_name or current_user.full_name or current_user.username,
            citizen_phone=payload.citizen_phone,
            category=payload.category,
            subject=payload.subject,
            description=payload.description,
            status="SUBMITTED",
            priority=payload.priority or "NORMAL",
            sla_due_date=now + timedelta(days=30),  # Statutory 30-day CPGRAMS timeline
        )

        saved = await self.grievance_repo.create_grievance(grievance)

        # Log initial creation audit history
        user_role = current_user.role_names[0] if current_user.role_names else "CITIZEN"
        await self.grievance_repo.add_history(
            grievance_id=saved.id,
            action="CREATED",
            from_status=None,
            to_status="SUBMITTED",
            performed_by_id=current_user.id,
            performed_by_name=current_user.full_name or current_user.username,
            performed_by_role=user_role,
            notes=f"Statutory grievance petition lodged under category '{payload.category}'.",
        )

        # Create system audit log
        await self.audit_repo.log_action(
            user_id=current_user.id,
            user_name=current_user.full_name or current_user.username,
            role=user_role,
            action="GRIEVANCE_LODGED",
            module="grievance",
            entity_type="Grievance",
            entity_id=saved.id,
            details=f"Grievance {saved.id} lodged for parcel {parcel.id} by {payload.citizen_name}.",
        )

        # Notify district revenue administration
        await self.audit_repo.create_notification(
            title="New Grievance Petition Lodged",
            message=f"Petition {saved.id} lodged on parcel {parcel.id} ({payload.category}).",
            category="grievance",
            recipient_role="DISTRICT_OFFICER",
            link_view="grievance",
        )

        # Re-fetch full entity with relations
        full_grievance = await self.grievance_repo.get_by_id(saved.id)
        return self._to_read_schema(full_grievance or saved)

    async def get_grievance(self, grievance_id: str, current_user: User) -> GrievanceRead:
        """Fetch grievance details with strict scoped data isolation."""
        grievance = await self.grievance_repo.get_by_id(grievance_id)
        if not grievance:
            raise EntityNotFoundException("Grievance", grievance_id)

        self._verify_access(current_user, grievance)
        return self._to_read_schema(grievance)

    async def list_grievances(
        self,
        current_user: User,
        filter_params: Optional[GrievanceFilter] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[GrievanceRead]:
        """List grievances applying citizen isolation or administrative geographic filters."""
        roles = set(r.upper() for r in current_user.role_names)

        if "CITIZEN" in roles:
            # Citizens strictly retrieve their own grievances
            records = await self.grievance_repo.list_grievances(
                filter_params=filter_params,
                citizen_user_id=current_user.id,
                skip=skip,
                limit=limit,
            )
        else:
            # Officers retrieve records strictly within their geographic and assignment jurisdiction
            allowed_states, allowed_districts, assigned_officer_id, _ = ScopeChecker.get_query_scope(current_user)
            records = await self.grievance_repo.list_grievances(
                filter_params=filter_params,
                allowed_states=allowed_states,
                allowed_districts=allowed_districts,
                assigned_officer_id=assigned_officer_id,
                skip=skip,
                limit=limit,
            )

        return [self._to_read_schema(g) for g in records]

    # -------------------------------------------------------------------------
    # 2. Administrative Actions: Assign, Update Status, Resolve, Attach Documents
    # -------------------------------------------------------------------------

    async def assign_grievance(
        self,
        grievance_id: str,
        payload: GrievanceAssignRequest,
        current_user: User,
    ) -> GrievanceRead:
        """Assign grievance to a specific revenue officer with status progression."""
        grievance = await self.grievance_repo.get_by_id(grievance_id)
        if not grievance:
            raise EntityNotFoundException("Grievance", grievance_id)

        self._verify_access(current_user, grievance)

        if grievance.status in ["RESOLVED", "REJECTED"]:
            raise ValidationException(
                f"Cannot assign officer to grievance {grievance_id} in terminal state '{grievance.status}'."
            )
        if grievance.status not in ["SUBMITTED", "OFFICER_ASSIGNED"]:
            raise ValidationException(
                f"Cannot assign officer to grievance {grievance_id} from state '{grievance.status}'. Only SUBMITTED or active assigned petitions can be allocated."
            )

        officer = await self.user_repo.get_by_id(payload.assigned_officer_id)
        if not officer:
            raise EntityNotFoundException("User", str(payload.assigned_officer_id))

        old_status = grievance.status
        new_status = "OFFICER_ASSIGNED"

        grievance.assigned_officer_id = officer.id
        grievance.assigned_officer_name = officer.full_name or officer.username
        grievance.assigned_date = datetime.now(timezone.utc)
        grievance.status = new_status

        user_role = current_user.role_names[0] if current_user.role_names else "OFFICER"
        await self.grievance_repo.add_history(
            grievance_id=grievance.id,
            action="ASSIGNED",
            from_status=old_status,
            to_status=new_status,
            performed_by_id=current_user.id,
            performed_by_name=current_user.full_name or current_user.username,
            performed_by_role=user_role,
            notes=payload.notes or f"Assigned to {officer.full_name or officer.username} for statutory inquiry.",
        )

        # Centralized audit logging
        await self.audit_repo.log_action(
            user_id=current_user.id,
            user_name=current_user.full_name or current_user.username,
            role=user_role,
            action="GRIEVANCE_ASSIGNED",
            module="grievance",
            entity_type="Grievance",
            entity_id=grievance.id,
            details=f"Assigned grievance {grievance.id} to officer {officer.full_name or officer.username} ({officer.id}).",
        )

        # Notify the assigned officer
        await self.audit_repo.create_notification(
            title="Grievance Hearing Assigned",
            message=f"You have been assigned to investigate petition {grievance.id} for parcel {grievance.parcel_id}.",
            category="grievance",
            user_id=officer.id,
            link_view="grievance",
        )

        # Notify the citizen petitioner
        if grievance.citizen_user_id:
            await self.audit_repo.create_notification(
                title="Grievance Status: Officer Assigned",
                message=f"Your petition {grievance.id} has been assigned to {officer.full_name or officer.username}.",
                category="grievance",
                user_id=grievance.citizen_user_id,
                link_view="grievance",
            )

        full = await self.grievance_repo.get_by_id(grievance.id)
        return self._to_read_schema(full or grievance)

    async def update_status(
        self,
        grievance_id: str,
        payload: GrievanceStatusUpdateRequest,
        current_user: User,
    ) -> GrievanceRead:
        """Update grievance lifecycle status with immutable history recording and state machine validation."""
        grievance = await self.grievance_repo.get_by_id(grievance_id)
        if not grievance:
            raise EntityNotFoundException("Grievance", grievance_id)

        self._verify_access(current_user, grievance)

        old_status = grievance.status
        new_status = payload.status

        if new_status not in VALID_GRIEVANCE_TRANSITIONS:
            raise ValidationException(
                f"Invalid grievance status: '{new_status}'. Allowed statuses: {list(VALID_GRIEVANCE_TRANSITIONS.keys())}"
            )

        if old_status in ["RESOLVED", "REJECTED"]:
            raise ValidationException(
                f"Cannot modify grievance {grievance_id} in terminal state '{old_status}'."
            )

        allowed = VALID_GRIEVANCE_TRANSITIONS.get(old_status, [])
        if new_status not in allowed:
            raise ValidationException(
                f"Illegal status transition from '{old_status}' to '{new_status}'. Allowed transitions: {allowed}"
            )

        grievance.status = new_status

        user_role = current_user.role_names[0] if current_user.role_names else "OFFICER"
        await self.grievance_repo.add_history(
            grievance_id=grievance.id,
            action="STATUS_UPDATED",
            from_status=old_status,
            to_status=payload.status,
            performed_by_id=current_user.id,
            performed_by_name=current_user.full_name or current_user.username,
            performed_by_role=user_role,
            notes=payload.notes or f"Status transitioned from {old_status} to {payload.status}.",
        )

        # Centralized audit logging
        await self.audit_repo.log_action(
            user_id=current_user.id,
            user_name=current_user.full_name or current_user.username,
            role=user_role,
            action="GRIEVANCE_STATUS_UPDATED",
            module="grievance",
            entity_type="Grievance",
            entity_id=grievance.id,
            details=f"Updated status of grievance {grievance.id} from {old_status} to {new_status}. Notes: {payload.notes or 'None'}",
        )

        # Notify petitioner
        if grievance.citizen_user_id:
            await self.audit_repo.create_notification(
                title=f"Grievance Status: {payload.status}",
                message=f"Petition {grievance.id} status is now {payload.status}. {payload.notes or ''}",
                category="grievance",
                user_id=grievance.citizen_user_id,
                link_view="grievance",
            )

        full = await self.grievance_repo.get_by_id(grievance.id)
        return self._to_read_schema(full or grievance)

    async def resolve_grievance(
        self,
        grievance_id: str,
        payload: GrievanceResolutionRequest,
        current_user: User,
    ) -> GrievanceRead:
        """Record formal inquiry findings and conclude grievance resolution."""
        grievance = await self.grievance_repo.get_by_id(grievance_id)
        if not grievance:
            raise EntityNotFoundException("Grievance", grievance_id)

        self._verify_access(current_user, grievance)

        old_status = grievance.status
        if old_status in ["RESOLVED", "REJECTED"]:
            raise ValidationException(
                f"Cannot resolve grievance {grievance_id} in terminal state '{old_status}'."
            )

        if old_status != "UNDER_REVIEW":
            raise ValidationException(
                f"Grievance {grievance_id} cannot be resolved directly from '{old_status}'. It must be in 'UNDER_REVIEW' stage before resolution."
            )

        new_status = "RESOLVED"

        grievance.status = new_status
        grievance.resolution_notes = payload.resolution_notes
        grievance.resolved_by_id = current_user.id
        grievance.resolved_by_name = current_user.full_name or current_user.username
        grievance.resolved_at = datetime.now(timezone.utc)

        user_role = current_user.role_names[0] if current_user.role_names else "OFFICER"
        await self.grievance_repo.add_history(
            grievance_id=grievance.id,
            action="RESOLUTION_ADDED",
            from_status=old_status,
            to_status=new_status,
            performed_by_id=current_user.id,
            performed_by_name=current_user.full_name or current_user.username,
            performed_by_role=user_role,
            notes=f"Resolution Finding: {payload.resolution_notes}",
        )

        # Centralized audit logging
        await self.audit_repo.log_action(
            user_id=current_user.id,
            user_name=current_user.full_name or current_user.username,
            role=user_role,
            action="GRIEVANCE_RESOLVED",
            module="grievance",
            entity_type="Grievance",
            entity_id=grievance.id,
            details=f"Resolved grievance {grievance.id}. Findings: {payload.resolution_notes}",
        )

        # Notify petitioner of resolution
        if grievance.citizen_user_id:
            await self.audit_repo.create_notification(
                title="Grievance Resolved",
                message=f"Petition {grievance.id} has been resolved by {current_user.full_name or current_user.username}.",
                category="grievance",
                user_id=grievance.citizen_user_id,
                link_view="grievance",
            )

        full = await self.grievance_repo.get_by_id(grievance.id)
        return self._to_read_schema(full or grievance)

    async def attach_document(
        self,
        grievance_id: str,
        document_name: str,
        file_bytes: bytes,
        mime_type: str,
        current_user: User,
    ) -> GrievanceDocumentRead:
        """Attach a supporting evidence document to a grievance petition."""
        grievance = await self.grievance_repo.get_by_id(grievance_id)
        if not grievance:
            raise EntityNotFoundException("Grievance", grievance_id)

        self._verify_access(current_user, grievance)

        sha256_hash = hashlib.sha256(file_bytes).hexdigest()
        file_size = len(file_bytes)
        virtual_path = f"grievances/{grievance.id}/{document_name}"

        doc = GrievanceDocument(
            id=uuid.uuid4(),
            grievance_id=grievance.id,
            document_name=document_name,
            file_path=virtual_path,
            file_size_bytes=file_size,
            mime_type=mime_type or "application/pdf",
            sha256_hash=sha256_hash,
            uploaded_by_id=current_user.id,
            uploaded_by_name=current_user.full_name or current_user.username,
            uploaded_at=datetime.now(timezone.utc),
        )

        saved = await self.grievance_repo.add_document(doc)

        user_role = current_user.role_names[0] if current_user.role_names else "CITIZEN"
        await self.grievance_repo.add_history(
            grievance_id=grievance.id,
            action="DOCUMENT_ATTACHED",
            from_status=grievance.status,
            to_status=grievance.status,
            performed_by_id=current_user.id,
            performed_by_name=current_user.full_name or current_user.username,
            performed_by_role=user_role,
            notes=f"Attached evidence document '{document_name}' ({round(file_size / 1024, 1)} KB).",
        )

        # Centralized audit logging
        await self.audit_repo.log_action(
            user_id=current_user.id,
            user_name=current_user.full_name or current_user.username,
            role=user_role,
            action="GRIEVANCE_DOCUMENT_ATTACHED",
            module="grievance",
            entity_type="Grievance",
            entity_id=grievance.id,
            details=f"Attached evidence document '{document_name}' ({file_size} bytes, SHA256: {sha256_hash[:16]}...) to grievance {grievance.id}.",
        )

        return GrievanceDocumentRead(
            id=saved.id,
            grievance_id=saved.grievance_id,
            document_name=saved.document_name,
            file_size_bytes=saved.file_size_bytes,
            mime_type=saved.mime_type,
            sha256_hash=saved.sha256_hash,
            uploaded_by_name=saved.uploaded_by_name,
            uploaded_at=saved.uploaded_at,
        )

