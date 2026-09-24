import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.rr import (
    AffectedFamily,
    ResettlementColony,
    RrBenefit,
    RrEligibility,
)
from app.schemas.rr import AffectedFamilyFilter


class RrRepository:
    """Repository handling database operations for Rehabilitation & Resettlement (R&R)."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_family_by_id(self, family_id: str) -> Optional[AffectedFamily]:
        """Fetch affected family with associated eligibility assessment and benefit entitlements."""
        stmt = (
            select(AffectedFamily)
            .where(AffectedFamily.id == family_id)
            .options(
                selectinload(AffectedFamily.project),
                selectinload(AffectedFamily.parcel),
                selectinload(AffectedFamily.eligibility),
                selectinload(AffectedFamily.benefits),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_family_by_citizen_user_id(self, citizen_user_id: uuid.UUID) -> Optional[AffectedFamily]:
        """Fetch affected family linked directly to an authenticated citizen user account."""
        stmt = (
            select(AffectedFamily)
            .where(AffectedFamily.citizen_user_id == citizen_user_id)
            .options(
                selectinload(AffectedFamily.project),
                selectinload(AffectedFamily.parcel),
                selectinload(AffectedFamily.eligibility),
                selectinload(AffectedFamily.benefits),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_affected_families(
        self,
        *,
        filter_params: Optional[AffectedFamilyFilter] = None,
        allowed_states: Optional[List[str]] = None,
        allowed_districts: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[AffectedFamily]:
        """List affected families constrained by jurisdictional scope."""
        stmt = select(AffectedFamily).options(
            selectinload(AffectedFamily.project),
            selectinload(AffectedFamily.parcel),
            selectinload(AffectedFamily.eligibility),
            selectinload(AffectedFamily.benefits),
        )

        if allowed_states is not None:
            stmt = stmt.where(AffectedFamily.state.in_(allowed_states))
        if allowed_districts is not None:
            stmt = stmt.where(AffectedFamily.district.in_(allowed_districts))

        if filter_params:
            if filter_params.state:
                stmt = stmt.where(AffectedFamily.state == filter_params.state)
            if filter_params.district:
                stmt = stmt.where(AffectedFamily.district == filter_params.district)
            if filter_params.project_id:
                stmt = stmt.where(AffectedFamily.project_id == filter_params.project_id)
            if filter_params.status:
                stmt = stmt.where(AffectedFamily.status == filter_params.status)
            if filter_params.affected_type:
                stmt = stmt.where(AffectedFamily.affected_type == filter_params.affected_type)

        stmt = stmt.order_by(AffectedFamily.created_at.desc()).offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def create_affected_family(self, family: AffectedFamily) -> AffectedFamily:
        """Persist a new affected family registration."""
        self.session.add(family)
        await self.session.flush()
        return family

    async def save_eligibility(self, eligibility: RrEligibility) -> RrEligibility:
        """Persist or update an R&R statutory eligibility record."""
        self.session.add(eligibility)
        await self.session.flush()
        return eligibility

    async def add_benefit(self, benefit: RrBenefit) -> RrBenefit:
        """Add an R&R benefit entitlement to an affected family."""
        self.session.add(benefit)
        await self.session.flush()
        return benefit

    async def get_benefit_by_id(self, benefit_id: uuid.UUID) -> Optional[RrBenefit]:
        """Fetch benefit by UUID."""
        stmt = (
            select(RrBenefit)
            .where(RrBenefit.id == benefit_id)
            .options(selectinload(RrBenefit.family))
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_resettlement_colonies(
        self,
        *,
        allowed_states: Optional[List[str]] = None,
        allowed_districts: Optional[List[str]] = None,
    ) -> List[ResettlementColony]:
        """List model resettlement colonies with social infrastructure and civic metrics."""
        stmt = select(ResettlementColony).options(selectinload(ResettlementColony.project))

        if allowed_states is not None:
            stmt = stmt.where(ResettlementColony.state.in_(allowed_states))
        if allowed_districts is not None:
            stmt = stmt.where(ResettlementColony.district.in_(allowed_districts))

        stmt = stmt.order_by(ResettlementColony.name.asc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_colony_by_id(self, colony_id: str) -> Optional[ResettlementColony]:
        """Fetch resettlement colony by ID."""
        stmt = (
            select(ResettlementColony)
            .where(ResettlementColony.id == colony_id)
            .options(selectinload(ResettlementColony.project))
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

