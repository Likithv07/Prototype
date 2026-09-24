import uuid
from typing import List, Optional
from sqlalchemy import desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.document import Document, DocumentVersion
from app.models.parcel import LandParcel
from app.models.project import Project


class DocumentRepository:
    """Repository handling statutory documents and immutable versioning revisions."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_document(self, document: Document) -> Document:
        self.session.add(document)
        await self.session.flush()
        await self.session.refresh(document)
        return document

    async def create_version(self, version: DocumentVersion) -> DocumentVersion:
        self.session.add(version)
        await self.session.flush()
        await self.session.refresh(version)
        return version

    async def get_document_by_id(self, document_id: str) -> Optional[Document]:
        stmt = (
            select(Document)
            .where(Document.id == document_id)
            .options(
                selectinload(Document.versions),
                selectinload(Document.project),
                selectinload(Document.parcel),
                selectinload(Document.uploader),
                selectinload(Document.verified_by),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_version_by_number(
        self,
        document_id: str,
        version_number: int,
    ) -> Optional[DocumentVersion]:
        stmt = (
            select(DocumentVersion)
            .where(
                DocumentVersion.document_id == document_id,
                DocumentVersion.version_number == version_number,
            )
            .options(selectinload(DocumentVersion.uploaded_by_user))
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_latest_version(self, document_id: str) -> Optional[DocumentVersion]:
        stmt = (
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(desc(DocumentVersion.version_number))
            .options(selectinload(DocumentVersion.uploaded_by_user))
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_documents(
        self,
        *,
        category: Optional[str] = None,
        project_id: Optional[str] = None,
        parcel_id: Optional[str] = None,
        uploader_id: Optional[uuid.UUID] = None,
        is_verified: Optional[bool] = None,
        allowed_states: Optional[List[str]] = None,
        allowed_districts: Optional[List[str]] = None,
        citizen_user_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Document]:
        stmt = (
            select(Document)
            .outerjoin(Document.parcel)
            .outerjoin(Document.project)
            .options(
                selectinload(Document.versions),
                selectinload(Document.project),
                selectinload(Document.parcel),
                selectinload(Document.uploader),
                selectinload(Document.verified_by),
            )
        )

        if category:
            stmt = stmt.where(Document.category == category)
        if project_id:
            stmt = stmt.where(Document.project_id == project_id)
        if parcel_id:
            stmt = stmt.where(Document.parcel_id == parcel_id)
        if uploader_id:
            stmt = stmt.where(Document.uploader_id == uploader_id)
        if is_verified is not None:
            stmt = stmt.where(Document.is_verified == is_verified)

        # Scoping constraints:
        # If citizen user, restrict to documents uploaded by them or attached to parcels owned by them
        if citizen_user_id:
            stmt = stmt.where(
                or_(
                    Document.uploader_id == citizen_user_id,
                    LandParcel.owner_user_id == citizen_user_id,
                )
            )

        if allowed_states:
            stmt = stmt.where(
                or_(
                    LandParcel.state.in_(allowed_states),
                    Project.state.in_(allowed_states),
                )
            )
        if allowed_districts:
            stmt = stmt.where(
                or_(
                    LandParcel.district.in_(allowed_districts),
                    Project.district.in_(allowed_districts),
                )
            )

        stmt = stmt.order_by(desc(Document.created_at)).offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def update_document(self, document: Document) -> Document:
        await self.session.flush()
        await self.session.refresh(document)
        return document

