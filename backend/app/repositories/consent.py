import uuid
from typing import List, Optional
from sqlalchemy import desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.consent import ConsentHistory, LandownerConsent
from app.models.parcel import LandParcel
from app.models.project import Project


class ConsentRepository:
    """Repository handling landowner consent records and lifecycle audit trails."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_consent(self, consent: LandownerConsent) -> LandownerConsent:
        self.session.add(consent)
        await self.session.flush()
        await self.session.refresh(consent)
        return consent

    async def get_consent_by_id(self, consent_id: str) -> Optional[LandownerConsent]:
        stmt = (
            select(LandownerConsent)
            .where(LandownerConsent.id == consent_id)
            .options(
                selectinload(LandownerConsent.parcel),
                selectinload(LandownerConsent.project),
                selectinload(LandownerConsent.landowner_user),
                selectinload(LandownerConsent.supporting_document),
                selectinload(LandownerConsent.verifying_officer),
                selectinload(LandownerConsent.history),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_by_parcel_id(self, parcel_id: str) -> Optional[LandownerConsent]:
        stmt = (
            select(LandownerConsent)
            .where(LandownerConsent.parcel_id == parcel_id)
            .options(
                selectinload(LandownerConsent.parcel),
                selectinload(LandownerConsent.project),
                selectinload(LandownerConsent.landowner_user),
                selectinload(LandownerConsent.supporting_document),
                selectinload(LandownerConsent.verifying_officer),
                selectinload(LandownerConsent.history),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    get_consent_by_parcel_id = get_by_parcel_id

    async def list_consents(
        self,
        *,
        project_id: Optional[str] = None,
        parcel_id: Optional[str] = None,
        status: Optional[str] = None,
        consent_type: Optional[str] = None,
        landowner_user_id: Optional[uuid.UUID] = None,
        allowed_states: Optional[List[str]] = None,
        allowed_districts: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[LandownerConsent]:
        stmt = (
            select(LandownerConsent)
            .join(LandownerConsent.parcel)
            .options(
                selectinload(LandownerConsent.parcel),
                selectinload(LandownerConsent.project),
                selectinload(LandownerConsent.landowner_user),
                selectinload(LandownerConsent.supporting_document),
                selectinload(LandownerConsent.verifying_officer),
                selectinload(LandownerConsent.history),
            )
        )

        if project_id:
            stmt = stmt.where(LandownerConsent.project_id == project_id)
        if parcel_id:
            stmt = stmt.where(LandownerConsent.parcel_id == parcel_id)
        if status:
            stmt = stmt.where(LandownerConsent.status == status)
        if consent_type:
            stmt = stmt.where(LandownerConsent.consent_type == consent_type)
        if landowner_user_id:
            stmt = stmt.where(
                or_(
                    LandownerConsent.landowner_user_id == landowner_user_id,
                    LandParcel.owner_user_id == landowner_user_id,
                )
            )

        if allowed_states:
            stmt = stmt.where(LandParcel.state.in_(allowed_states))
        if allowed_districts:
            stmt = stmt.where(LandParcel.district.in_(allowed_districts))

        stmt = stmt.order_by(desc(LandownerConsent.created_at)).offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def add_history(self, history: ConsentHistory) -> ConsentHistory:
        self.session.add(history)
        await self.session.flush()
        await self.session.refresh(history)
        return history

    async def get_history(self, consent_id: str) -> List[ConsentHistory]:
        stmt = (
            select(ConsentHistory)
            .where(ConsentHistory.consent_id == consent_id)
            .order_by(ConsentHistory.timestamp.asc())
            .options(selectinload(ConsentHistory.performed_by))
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def update_consent(self, consent: LandownerConsent) -> LandownerConsent:
        await self.session.flush()
        await self.session.refresh(consent)
        return consent

