import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.grievance import (
    Grievance,
    GrievanceDocument,
    GrievanceHistory,
)
from app.models.parcel import LandParcel
from app.schemas.grievance import GrievanceFilter


class GrievanceRepository:
    """Repository handling database operations for statutory grievance petitions."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, grievance_id: str) -> Optional[Grievance]:
        """Fetch grievance by ID with associated documents, history, parcel, and project."""
        stmt = (
            select(Grievance)
            .where(Grievance.id == grievance_id)
            .options(
                selectinload(Grievance.parcel),
                selectinload(Grievance.project),
                selectinload(Grievance.documents),
                selectinload(Grievance.history),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def create_grievance(self, grievance: Grievance) -> Grievance:
        """Persist a new grievance petition."""
        self.session.add(grievance)
        await self.session.flush()
        return grievance

    async def list_grievances(
        self,
        *,
        filter_params: Optional[GrievanceFilter] = None,
        allowed_states: Optional[List[str]] = None,
        allowed_districts: Optional[List[str]] = None,
        assigned_officer_id: Optional[uuid.UUID] = None,
        citizen_user_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Grievance]:
        """List grievances filtered by multi-tier jurisdictional, assignment, and citizen ownership scopes."""
        stmt = (
            select(Grievance)
            .join(LandParcel, Grievance.parcel_id == LandParcel.id)
            .options(
                selectinload(Grievance.parcel),
                selectinload(Grievance.project),
                selectinload(Grievance.documents),
                selectinload(Grievance.history),
            )
        )

        # Scoped geographic filtering
        if allowed_states is not None:
            stmt = stmt.where(LandParcel.state.in_(allowed_states))
        if allowed_districts is not None:
            stmt = stmt.where(LandParcel.district.in_(allowed_districts))
        if assigned_officer_id is not None:
            stmt = stmt.where(LandParcel.assigned_officer_id == assigned_officer_id)

        # Citizen isolation: Citizens must only view their own grievances
        if citizen_user_id is not None:
            stmt = stmt.where(Grievance.citizen_user_id == citizen_user_id)

        # Optional query filters
        if filter_params:
            if filter_params.status:
                stmt = stmt.where(Grievance.status == filter_params.status)
            if filter_params.category:
                stmt = stmt.where(Grievance.category == filter_params.category)
            if filter_params.parcel_id:
                stmt = stmt.where(Grievance.parcel_id == filter_params.parcel_id)
            if filter_params.project_id:
                stmt = stmt.where(Grievance.project_id == filter_params.project_id)
            if filter_params.district:
                stmt = stmt.where(LandParcel.district == filter_params.district)

        stmt = stmt.order_by(Grievance.created_at.desc()).offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def add_history(
        self,
        *,
        grievance_id: str,
        action: str,
        from_status: Optional[str] = None,
        to_status: Optional[str] = None,
        performed_by_id: Optional[uuid.UUID] = None,
        performed_by_name: str,
        performed_by_role: str,
        notes: Optional[str] = None,
    ) -> GrievanceHistory:
        """Append an immutable audit entry to grievance history."""
        entry = GrievanceHistory(
            grievance_id=grievance_id,
            action=action,
            from_status=from_status,
            to_status=to_status,
            performed_by_id=performed_by_id,
            performed_by_name=performed_by_name,
            performed_by_role=performed_by_role,
            notes=notes,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def add_document(self, document: GrievanceDocument) -> GrievanceDocument:
        """Attach a supporting evidence document to a grievance petition."""
        self.session.add(document)
        await self.session.flush()
        return document

