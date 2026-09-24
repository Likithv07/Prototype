"""SQLAlchemy models package for BhoomiSetu."""
from app.models.audit import AuditLog, Notification
from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.compensation import (
    Award,
    CompensationAssessment,
    CompensationComponent,
    CompensationHistory,
    CompensationRule,
)
from app.models.consent import ConsentHistory, LandownerConsent
from app.models.document import Document, DocumentVersion
from app.models.field import (
    FieldAssignment,
    FieldDocument,
    FieldPhoto,
    FieldSurveyRecord,
)
from app.models.parcel import LandParcel
from app.models.project import Project
from app.models.user import Permission, Role, User, role_permissions, user_roles
from app.models.workflow import (
    WorkflowDefinition,
    WorkflowInstance,
    WorkflowStageDefinition,
    WorkflowTransitionDefinition,
    WorkflowTransitionHistory,
)

from app.models.grievance import Grievance, GrievanceDocument, GrievanceHistory
from app.models.rr import (
    AffectedFamily,
    ResettlementColony,
    RrBenefit,
    RrEligibility,
)

__all__ = [
    "Base",
    "TimestampMixin",
    "UUIDMixin",
    "User",
    "Role",
    "Permission",
    "user_roles",
    "role_permissions",
    "Project",
    "LandParcel",
    "WorkflowDefinition",
    "WorkflowStageDefinition",
    "WorkflowTransitionDefinition",
    "WorkflowInstance",
    "WorkflowTransitionHistory",
    "AuditLog",
    "Notification",
    "FieldAssignment",
    "FieldSurveyRecord",
    "FieldPhoto",
    "FieldDocument",
    "Document",
    "DocumentVersion",
    "LandownerConsent",
    "ConsentHistory",
    "CompensationRule",
    "CompensationAssessment",
    "CompensationComponent",
    "Award",
    "CompensationHistory",
    "Grievance",
    "GrievanceDocument",
    "GrievanceHistory",
    "AffectedFamily",
    "RrEligibility",
    "RrBenefit",
    "ResettlementColony",
]
