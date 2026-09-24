import uuid
from typing import List, Optional
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.field import (
    FieldAssignment,
    FieldDocument,
    FieldPhoto,
    FieldSurveyRecord,
)
from app.models.parcel import LandParcel


class FieldRepository:
    """Repository handling field assignments, survey enumeration, photos, and documents."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # -------------------------------------------------------------------------
    # Field Assignments
    # -------------------------------------------------------------------------

    async def create_assignment(self, assignment: FieldAssignment) -> FieldAssignment:
        self.session.add(assignment)
        await self.session.flush()
        await self.session.refresh(assignment)
        return assignment

    async def get_assignment_by_id(self, assignment_id: str) -> Optional[FieldAssignment]:
        stmt = (
            select(FieldAssignment)
            .where(FieldAssignment.id == assignment_id)
            .options(
                selectinload(FieldAssignment.parcel),
                selectinload(FieldAssignment.project),
                selectinload(FieldAssignment.assigned_officer),
                selectinload(FieldAssignment.photos),
                selectinload(FieldAssignment.documents),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_assignments(
        self,
        *,
        assigned_officer_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        project_id: Optional[str] = None,
        parcel_id: Optional[str] = None,
        allowed_states: Optional[List[str]] = None,
        allowed_districts: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[FieldAssignment]:
        stmt = select(FieldAssignment).join(FieldAssignment.parcel).options(
            selectinload(FieldAssignment.parcel),
            selectinload(FieldAssignment.project),
            selectinload(FieldAssignment.assigned_officer),
        )

        if assigned_officer_id:
            stmt = stmt.where(FieldAssignment.assigned_officer_id == assigned_officer_id)
        if status:
            stmt = stmt.where(FieldAssignment.status.ilike(status))
        if priority:
            stmt = stmt.where(FieldAssignment.priority.ilike(priority))
        if project_id:
            stmt = stmt.where(FieldAssignment.project_id == project_id)
        if parcel_id:
            stmt = stmt.where(FieldAssignment.parcel_id == parcel_id)

        # Scoped geographic constraints on parent parcel
        if allowed_states is not None:
            stmt = stmt.where(LandParcel.state.in_(allowed_states))
        if allowed_districts is not None:
            stmt = stmt.where(LandParcel.district.in_(allowed_districts))

        stmt = stmt.order_by(FieldAssignment.assigned_date.desc()).offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    # -------------------------------------------------------------------------
    # Field Survey Records
    # -------------------------------------------------------------------------

    async def create_survey_record(self, survey: FieldSurveyRecord) -> FieldSurveyRecord:
        self.session.add(survey)
        await self.session.flush()
        await self.session.refresh(survey)
        return survey

    async def get_survey_by_id(self, survey_id: str) -> Optional[FieldSurveyRecord]:
        stmt = (
            select(FieldSurveyRecord)
            .where(FieldSurveyRecord.id == survey_id)
            .options(
                selectinload(FieldSurveyRecord.parcel),
                selectinload(FieldSurveyRecord.officer),
                selectinload(FieldSurveyRecord.verified_by),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_surveys(
        self,
        *,
        parcel_id: Optional[str] = None,
        project_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[FieldSurveyRecord]:
        stmt = select(FieldSurveyRecord).options(
            selectinload(FieldSurveyRecord.parcel),
            selectinload(FieldSurveyRecord.officer),
        )
        if parcel_id:
            stmt = stmt.where(FieldSurveyRecord.parcel_id == parcel_id)
        if project_id:
            stmt = stmt.where(FieldSurveyRecord.project_id == project_id)
        stmt = stmt.order_by(FieldSurveyRecord.survey_date.desc()).offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    # -------------------------------------------------------------------------
    # Field Photos
    # -------------------------------------------------------------------------

    async def create_photo(self, photo: FieldPhoto) -> FieldPhoto:
        self.session.add(photo)
        await self.session.flush()
        await self.session.refresh(photo)
        return photo

    async def get_photo_by_id(self, photo_id: str) -> Optional[FieldPhoto]:
        stmt = select(FieldPhoto).where(FieldPhoto.id == photo_id)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_photos(
        self,
        *,
        parcel_id: Optional[str] = None,
        assignment_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[FieldPhoto]:
        stmt = select(FieldPhoto)
        if parcel_id:
            stmt = stmt.where(FieldPhoto.parcel_id == parcel_id)
        if assignment_id:
            stmt = stmt.where(FieldPhoto.assignment_id == assignment_id)
        if status:
            stmt = stmt.where(FieldPhoto.status.ilike(status))
        stmt = stmt.order_by(FieldPhoto.captured_at.desc()).offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    # -------------------------------------------------------------------------
    # Field Documents
    # -------------------------------------------------------------------------

    async def create_document(self, document: FieldDocument) -> FieldDocument:
        self.session.add(document)
        await self.session.flush()
        await self.session.refresh(document)
        return document

    async def get_document_by_id(self, doc_id: str) -> Optional[FieldDocument]:
        stmt = select(FieldDocument).where(FieldDocument.id == doc_id)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_documents(
        self,
        *,
        parcel_id: Optional[str] = None,
        assignment_id: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[FieldDocument]:
        stmt = select(FieldDocument)
        if parcel_id:
            stmt = stmt.where(FieldDocument.parcel_id == parcel_id)
        if assignment_id:
            stmt = stmt.where(FieldDocument.assignment_id == assignment_id)
        if category:
            stmt = stmt.where(FieldDocument.category.ilike(category))
        if status:
            stmt = stmt.where(FieldDocument.status.ilike(status))
        stmt = stmt.order_by(FieldDocument.created_at.desc()).offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

