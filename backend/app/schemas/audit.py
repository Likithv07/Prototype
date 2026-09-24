import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AuditLogRead(BaseModel):
    """Audit log entry response schema."""

    id: uuid.UUID
    user_name: str
    role: str
    action: str
    module: str
    entity_type: str
    entity_id: str
    details: str
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationRead(BaseModel):
    """Notification response schema."""

    id: uuid.UUID
    recipient_role: Optional[str] = None
    title: str
    message: str
    category: str
    link_view: Optional[str] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

