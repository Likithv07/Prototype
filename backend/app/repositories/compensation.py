import uuid
from typing import List, Optional
from sqlalchemy import desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.compensation import (
    Award,
    CompensationAssessment,
    CompensationComponent,
    CompensationHistory,
    CompensationRule,
)
from app.models.parcel import LandParcel
from app.models.project import Project


class CompensationRepository:
    """Repository handling versioned compensation rules, assessments, itemized components, and awards."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # -------------------------------------------------------------------------
    # Compensation Rules
    # -------------------------------------------------------------------------

    async def get_active_rule(
        self,
        *,
        rule_id: Optional[str] = None,
        state: Optional[str] = None,
    ) -> Optional[CompensationRule]:
        if rule_id:
            stmt = select(CompensationRule).where(CompensationRule.id == rule_id)
            res = await self.session.execute(stmt)
            rule = res.scalars().first()
            if rule:
                return rule

        # State override check
        if state:
            stmt = (
                select(CompensationRule)
                .where(CompensationRule.state == state, CompensationRule.is_active == True)
                .order_by(desc(CompensationRule.created_at))
            )
            res = await self.session.execute(stmt)
            rule = res.scalars().first()
            if rule:
                return rule

        # Central / national default rule (state is None)
        stmt = (
            select(CompensationRule)
            .where(CompensationRule.state == None, CompensationRule.is_active == True)
            .order_by(desc(CompensationRule.created_at))
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def create_rule(self, rule: CompensationRule) -> CompensationRule:
        self.session.add(rule)
        await self.session.flush()
        await self.session.refresh(rule)
        return rule

    # -------------------------------------------------------------------------
    # Compensation Assessments
    # -------------------------------------------------------------------------

    async def create_assessment(self, assessment: CompensationAssessment) -> CompensationAssessment:
        self.session.add(assessment)
        await self.session.flush()
        await self.session.refresh(assessment)
        return assessment

    async def get_assessment_by_id(self, assessment_id: str) -> Optional[CompensationAssessment]:
        stmt = (
            select(CompensationAssessment)
            .where(CompensationAssessment.id == assessment_id)
            .options(
                selectinload(CompensationAssessment.parcel),
                selectinload(CompensationAssessment.project),
                selectinload(CompensationAssessment.rule),
                selectinload(CompensationAssessment.components),
                selectinload(CompensationAssessment.award),
                selectinload(CompensationAssessment.history),
                selectinload(CompensationAssessment.calculated_by),
                selectinload(CompensationAssessment.approved_by),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_assessment_by_parcel_id(self, parcel_id: str) -> Optional[CompensationAssessment]:
        stmt = (
            select(CompensationAssessment)
            .where(CompensationAssessment.parcel_id == parcel_id)
            .options(
                selectinload(CompensationAssessment.parcel),
                selectinload(CompensationAssessment.project),
                selectinload(CompensationAssessment.rule),
                selectinload(CompensationAssessment.components),
                selectinload(CompensationAssessment.award),
                selectinload(CompensationAssessment.history),
                selectinload(CompensationAssessment.calculated_by),
                selectinload(CompensationAssessment.approved_by),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_assessments(
        self,
        *,
        project_id: Optional[str] = None,
        parcel_id: Optional[str] = None,
        status: Optional[str] = None,
        landowner_id: Optional[uuid.UUID] = None,
        allowed_states: Optional[List[str]] = None,
        allowed_districts: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[CompensationAssessment]:
        stmt = (
            select(CompensationAssessment)
            .join(CompensationAssessment.parcel)
            .options(
                selectinload(CompensationAssessment.parcel),
                selectinload(CompensationAssessment.project),
                selectinload(CompensationAssessment.rule),
                selectinload(CompensationAssessment.components),
                selectinload(CompensationAssessment.award),
                selectinload(CompensationAssessment.history),
            )
        )

        if project_id:
            stmt = stmt.where(CompensationAssessment.project_id == project_id)
        if parcel_id:
            stmt = stmt.where(CompensationAssessment.parcel_id == parcel_id)
        if status:
            stmt = stmt.where(CompensationAssessment.status == status)
        if landowner_id:
            stmt = stmt.where(
                or_(
                    CompensationAssessment.landowner_id == landowner_id,
                    LandParcel.owner_user_id == landowner_id,
                )
            )

        if allowed_states:
            stmt = stmt.where(LandParcel.state.in_(allowed_states))
        if allowed_districts:
            stmt = stmt.where(LandParcel.district.in_(allowed_districts))

        stmt = stmt.order_by(desc(CompensationAssessment.created_at)).offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def update_assessment(self, assessment: CompensationAssessment) -> CompensationAssessment:
        await self.session.flush()
        await self.session.refresh(assessment)
        return assessment

    # -------------------------------------------------------------------------
    # Compensation Components
    # -------------------------------------------------------------------------

    async def add_component(self, component: CompensationComponent) -> CompensationComponent:
        self.session.add(component)
        await self.session.flush()
        await self.session.refresh(component)
        return component

    # -------------------------------------------------------------------------
    # Awards
    # -------------------------------------------------------------------------

    async def create_award(self, award: Award) -> Award:
        self.session.add(award)
        await self.session.flush()
        await self.session.refresh(award)
        return award

    async def get_award_by_id(self, award_id: str) -> Optional[Award]:
        stmt = (
            select(Award)
            .where(Award.id == award_id)
            .options(
                selectinload(Award.assessment),
                selectinload(Award.parcel),
                selectinload(Award.project),
                selectinload(Award.competent_authority),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    # -------------------------------------------------------------------------
    # History Ledger
    # -------------------------------------------------------------------------

    async def add_history(self, history: CompensationHistory) -> CompensationHistory:
        self.session.add(history)
        await self.session.flush()
        await self.session.refresh(history)
        return history

    async def get_history(self, assessment_id: str) -> List[CompensationHistory]:
        stmt = (
            select(CompensationHistory)
            .where(CompensationHistory.assessment_id == assessment_id)
            .order_by(CompensationHistory.timestamp.asc())
            .options(selectinload(CompensationHistory.performed_by))
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

