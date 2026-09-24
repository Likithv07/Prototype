import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import AuditLog, Notification
from app.repositories.base import BaseRepository


class AuditRepository:
    """Repository handling immutable audit logging and notifications."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_action(
        self,
        *,
        user_id: Optional[uuid.UUID] = None,
        user_name: str,
        role: str,
        action: str,
        module: str = "workflow",
        entity_type: str,
        entity_id: str,
        details: str,
    ) -> AuditLog:
        """Persist an immutable audit log entry."""
        audit_entry = AuditLog(
            user_id=user_id,
            user_name=user_name,
            role=role,
            action=action,
            module=module,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
        )
        self.session.add(audit_entry)
        await self.session.flush()
        return audit_entry

    async def create_notification(
        self,
        *,
        title: str,
        message: str,
        category: str = "workflow",
        recipient_role: Optional[str] = None,
        user_id: Optional[uuid.UUID] = None,
        link_view: Optional[str] = None,
    ) -> Notification:
        """Create a targeted in-app notification."""
        notif = Notification(
            title=title,
            message=message,
            category=category,
            recipient_role=recipient_role,
            user_id=user_id,
            link_view=link_view,
        )
        self.session.add(notif)
        await self.session.flush()
        return notif

    async def list_audit_logs(
        self,
        *,
        entity_id: Optional[str] = None,
        module: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[AuditLog]:
        """Fetch paginated audit entries."""
        stmt = select(AuditLog)
        if entity_id:
            stmt = stmt.where(AuditLog.entity_id == entity_id)
        if module:
            stmt = stmt.where(AuditLog.module == module)
        stmt = stmt.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def list_user_notifications(
        self,
        user_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Notification]:
        """Fetch notifications specifically addressed to a user."""
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def mark_notification_as_read(
        self,
        notification_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[Notification]:
        """Mark a notification as read if it belongs to the user."""
        stmt = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
        res = await self.session.execute(stmt)
        notif = res.scalars().first()
        if notif:
            notif.is_read = True
            await self.session.flush()
        return notif

