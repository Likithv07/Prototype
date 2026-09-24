import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
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
from app.models.document import Document, DocumentVersion
from app.models.user import User
from app.repositories.audit import AuditRepository
from app.repositories.document import DocumentRepository
from app.repositories.parcel import ParcelRepository
from app.repositories.project import ProjectRepository
from app.schemas.document import (
    DocumentCreate,
    DocumentRead,
    DocumentVerificationRequest,
    DocumentVersionRead,
)

logger = get_logger(__name__)


class DocumentService:
    """Service orchestrating statutory document management, immutable versioning, and verification."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.doc_repo = DocumentRepository(session)
        self.parcel_repo = ParcelRepository(session)
        self.project_repo = ProjectRepository(session)
        self.audit_repo = AuditRepository(session)
        self.storage = get_storage_provider()

    def _verify_document_access(self, user: User, document: Document) -> None:
        """Enforce scoped authorization for accessing or downloading statutory documents."""
        if "ADMIN" in user.role_names or "CENTRAL_OFFICIAL" in user.role_names:
            return

        if "CITIZEN" in user.role_names:
            # Citizens can only access documents they uploaded or attached to parcels they own
            if document.uploader_id == user.id:
                return
            if document.parcel and document.parcel.owner_user_id == user.id:
                return
            raise ForbiddenException(
                "Access denied: Citizens may only access their own statutory records."
            )

        # State/District/Field officers are verified against parcel or project geography
        if document.parcel:
            ScopeChecker.verify_parcel_access(user, document.parcel)
        elif document.project:
            ScopeChecker.verify_project_access(user, document.project)

    def _to_version_read(self, version: DocumentVersion) -> DocumentVersionRead:
        return DocumentVersionRead(
            id=version.id,
            document_id=version.document_id,
            version_number=version.version_number,
            version_label=version.version_label,
            filename=version.filename,
            file_size_bytes=version.file_size_bytes,
            mime_type=version.mime_type,
            checksum_sha256=version.checksum_sha256,
            file_url=version.file_url,
            changelog=version.changelog,
            uploaded_by_id=version.uploaded_by_id,
            created_at=version.created_at,
        )

    def _to_document_read(self, doc: Document) -> DocumentRead:
        version_reads = [self._to_version_read(v) for v in (doc.versions or [])]
        latest = version_reads[0] if version_reads else None
        return DocumentRead(
            id=doc.id,
            title=doc.title,
            category=doc.category,
            project_id=doc.project_id,
            parcel_id=doc.parcel_id,
            uploader_id=doc.uploader_id,
            uploaded_by=doc.uploaded_by,
            current_version=doc.current_version,
            is_verified=doc.is_verified,
            verified_by_id=doc.verified_by_id,
            verified_at=doc.verified_at,
            verification_remarks=doc.verification_remarks,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
            versions=version_reads,
            latest_version=latest,
        )

    async def create_document(
        self,
        *,
        file_bytes: bytes,
        filename: str,
        doc_in: DocumentCreate,
        current_user: User,
    ) -> DocumentRead:
        """Register a new document and store its initial version (v1.0)."""
        # Validate magic bytes and compute cryptographic checksum
        detected_mime = validate_file_magic_bytes(file_bytes, filename)
        checksum = compute_sha256(file_bytes)

        # Verify context associations & scope if project or parcel provided
        if doc_in.parcel_id:
            parcel = await self.parcel_repo.get_by_id(doc_in.parcel_id)
            if not parcel:
                raise EntityNotFoundException("LandParcel", doc_in.parcel_id)
            ScopeChecker.verify_parcel_access(current_user, parcel)
            # Infer project_id from parcel if omitted
            if not doc_in.project_id:
                doc_in.project_id = parcel.project_id

        if doc_in.project_id:
            project = await self.project_repo.get_by_id(doc_in.project_id)
            if not project:
                raise EntityNotFoundException("Project", doc_in.project_id)
            ScopeChecker.verify_project_access(current_user, project)

        doc_id = doc_in.id or f"DOC-{datetime.now(timezone.utc).year}-{uuid.uuid4().hex[:8].upper()}"

        existing = await self.doc_repo.get_document_by_id(doc_id)
        if existing:
            raise EntityAlreadyExistsException("Document", doc_id)

        # Upload initial file version to storage provider
        storage_key, file_url = await self.storage.upload_file(
            file_bytes=file_bytes,
            filename=filename,
            content_type=detected_mime,
            directory=f"statutory/{doc_id}",
        )

        doc = Document(
            id=doc_id,
            title=doc_in.title,
            category=doc_in.category,
            project_id=doc_in.project_id,
            parcel_id=doc_in.parcel_id,
            uploader_id=current_user.id,
            uploaded_by=current_user.full_name,
            current_version=1,
            is_verified=False,
        )
        created_doc = await self.doc_repo.create_document(doc)

        v1 = DocumentVersion(
            document_id=doc_id,
            version_number=1,
            version_label="v1.0",
            storage_key=storage_key,
            filename=filename,
            file_size_bytes=len(file_bytes),
            mime_type=detected_mime,
            checksum_sha256=checksum,
            file_url=file_url,
            changelog="Initial statutory filing",
            uploaded_by_id=current_user.id,
        )
        await self.doc_repo.create_version(v1)

        await self.audit_repo.log_action(
            user_id=current_user.id,
            user_name=current_user.full_name,
            role=current_user.role_names[0] if current_user.role_names else "OFFICER",
            action="DOCUMENT_UPLOADED",
            module="documents",
            entity_type="Document",
            entity_id=doc_id,
            details=f"Document '{doc_in.title}' ({doc_in.category}) v1.0 created. Checksum: {checksum[:16]}...",
        )

        fresh_doc = await self.doc_repo.get_document_by_id(doc_id)
        return self._to_document_read(fresh_doc or created_doc)

    async def add_version(
        self,
        *,
        document_id: str,
        file_bytes: bytes,
        filename: str,
        changelog: Optional[str],
        current_user: User,
    ) -> DocumentRead:
        """Add an immutable new version revision to an existing document. Existing files are NEVER overwritten."""
        doc = await self.doc_repo.get_document_by_id(document_id)
        if not doc:
            raise EntityNotFoundException("Document", document_id)

        self._verify_document_access(current_user, doc)

        detected_mime = validate_file_magic_bytes(file_bytes, filename)
        checksum = compute_sha256(file_bytes)

        next_version_num = doc.current_version + 1
        version_label = f"v{next_version_num}.0"

        storage_key, file_url = await self.storage.upload_file(
            file_bytes=file_bytes,
            filename=filename,
            content_type=detected_mime,
            directory=f"statutory/{document_id}",
        )

        new_version = DocumentVersion(
            document_id=document_id,
            version_number=next_version_num,
            version_label=version_label,
            storage_key=storage_key,
            filename=filename,
            file_size_bytes=len(file_bytes),
            mime_type=detected_mime,
            checksum_sha256=checksum,
            file_url=file_url,
            changelog=changelog or f"Revision {version_label}",
            uploaded_by_id=current_user.id,
        )
        await self.doc_repo.create_version(new_version)

        # Update master record: bump version number and reset verification state for new version
        doc.current_version = next_version_num
        doc.is_verified = False
        doc.verified_by_id = None
        doc.verified_at = None
        doc.verification_remarks = f"Pending re-verification for {version_label}"
        await self.doc_repo.update_document(doc)

        await self.audit_repo.log_action(
            user_id=current_user.id,
            user_name=current_user.full_name,
            role=current_user.role_names[0] if current_user.role_names else "OFFICER",
            action="DOCUMENT_VERSION_ADDED",
            module="documents",
            entity_type="DocumentVersion",
            entity_id=f"{document_id}-{version_label}",
            details=f"Revision {version_label} added for document '{doc.title}'. Checksum: {checksum[:16]}...",
        )

        refreshed = await self.doc_repo.get_document_by_id(document_id)
        return self._to_document_read(refreshed or doc)

    async def get_document(self, document_id: str, current_user: User) -> DocumentRead:
        """Retrieve statutory document details with version history after authorization check."""
        doc = await self.doc_repo.get_document_by_id(document_id)
        if not doc:
            raise EntityNotFoundException("Document", document_id)

        self._verify_document_access(current_user, doc)
        return self._to_document_read(doc)

    async def list_documents(
        self,
        *,
        category: Optional[str] = None,
        project_id: Optional[str] = None,
        parcel_id: Optional[str] = None,
        uploader_id: Optional[uuid.UUID] = None,
        is_verified: Optional[bool] = None,
        current_user: User,
        skip: int = 0,
        limit: int = 50,
    ) -> List[DocumentRead]:
        """List documents filtered by category, project, parcel, and current user scope."""
        citizen_user_id = None
        allowed_states = None
        allowed_districts = None

        if "CITIZEN" in current_user.role_names:
            citizen_user_id = current_user.id
        elif "ADMIN" not in current_user.role_names and "CENTRAL_OFFICIAL" not in current_user.role_names:
            allowed_states = current_user.states or None
            allowed_districts = current_user.districts or None

        docs = await self.doc_repo.list_documents(
            category=category,
            project_id=project_id,
            parcel_id=parcel_id,
            uploader_id=uploader_id,
            is_verified=is_verified,
            allowed_states=allowed_states,
            allowed_districts=allowed_districts,
            citizen_user_id=citizen_user_id,
            skip=skip,
            limit=limit,
        )
        return [self._to_document_read(d) for d in docs]

    async def get_download_file(
        self,
        document_id: str,
        version_number: Optional[int],
        current_user: User,
    ) -> Tuple[bytes, str, str, str]:
        """Download document bytes for authorized users. Returns (file_bytes, filename, mime_type, sha256)."""
        doc = await self.doc_repo.get_document_by_id(document_id)
        if not doc:
            raise EntityNotFoundException("Document", document_id)

        self._verify_document_access(current_user, doc)

        target_version = None
        if version_number is not None:
            target_version = await self.doc_repo.get_version_by_number(document_id, version_number)
        else:
            target_version = await self.doc_repo.get_latest_version(document_id)

        if not target_version:
            raise EntityNotFoundException(
                "DocumentVersion",
                f"{document_id} (version {version_number or 'latest'})",
            )

        file_bytes = await self.storage.download_file(target_version.storage_key)
        return file_bytes, target_version.filename, target_version.mime_type, target_version.checksum_sha256

    async def verify_document(
        self,
        *,
        document_id: str,
        verify_in: DocumentVerificationRequest,
        current_user: User,
    ) -> DocumentRead:
        """Officers verify or reject document authenticity."""
        if "CITIZEN" in current_user.role_names and "ADMIN" not in current_user.role_names:
            raise ForbiddenException("Citizens cannot verify statutory documents.")

        doc = await self.doc_repo.get_document_by_id(document_id)
        if not doc:
            raise EntityNotFoundException("Document", document_id)

        self._verify_document_access(current_user, doc)

        doc.is_verified = verify_in.is_verified
        doc.verified_by_id = current_user.id
        doc.verified_at = datetime.now(timezone.utc)
        doc.verification_remarks = verify_in.verification_remarks
        await self.doc_repo.update_document(doc)

        action = "DOCUMENT_VERIFIED" if verify_in.is_verified else "DOCUMENT_REJECTED"
        await self.audit_repo.log_action(
            user_id=current_user.id,
            user_name=current_user.full_name,
            role=current_user.role_names[0] if current_user.role_names else "OFFICER",
            action=action,
            module="documents",
            entity_type="Document",
            entity_id=doc.id,
            details=f"Document '{doc.title}' set to is_verified={verify_in.is_verified}. Remarks: {verify_in.verification_remarks}",
        )

        refreshed = await self.doc_repo.get_document_by_id(document_id)
        return self._to_document_read(refreshed or doc)

