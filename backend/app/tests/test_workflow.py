import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import status
from httpx import AsyncClient
from app.api.deps import get_current_user, get_db
from app.core.security import hash_password
from app.main import app
from app.models.project import Project
from app.models.user import Role, User
from app.models.workflow import (
    WorkflowDefinition,
    WorkflowInstance,
    WorkflowStageDefinition,
    WorkflowTransitionDefinition,
    WorkflowTransitionHistory,
)
from app.repositories.workflow import STATUTORY_STAGES, STATUTORY_TRANSITIONS

pytestmark = pytest.mark.asyncio

CENTRAL_USER_ID = uuid.uuid4()
STATE_TS_USER_ID = uuid.uuid4()
DISTRICT_HYD_USER_ID = uuid.uuid4()
CITIZEN_USER_ID = uuid.uuid4()


def build_test_user(user_id: uuid.UUID, username: str, role_name: str, state: str = None, district: str = None) -> User:
    role = Role(id=uuid.uuid4(), name=role_name, is_system_role=True)
    user = User(
        id=user_id,
        email=f"{username}@bhoomi.gov.in",
        username=username,
        hashed_password=hash_password("Pass123!"),
        full_name=f"{username.title()} User",
        is_active=True,
        is_verified=True,
        state=state,
        district=district,
    )
    user.roles = [role]
    return user


def build_mock_workflow_definition() -> WorkflowDefinition:
    wf_def_id = uuid.uuid4()
    wf_def = WorkflowDefinition(
        id=wf_def_id,
        code="STANDARD_RFCTLARR_2013",
        name="Standard RFCTLARR 2013 Statutory Lifecycle",
        is_active=True,
        is_default=True,
        stages=[],
        transitions=[],
    )

    for order, code, name, desc, role, sla, initial, terminal in STATUTORY_STAGES:
        stage = WorkflowStageDefinition(
            id=uuid.uuid4(),
            workflow_definition_id=wf_def_id,
            stage_code=code,
            name=name,
            description=desc,
            stage_order=order,
            required_role=role,
            sla_days=sla,
            is_initial=initial,
            is_terminal=terminal,
        )
        wf_def.stages.append(stage)

    for from_code, to_code, action, desc, role, perm, req_remarks in STATUTORY_TRANSITIONS:
        trans = WorkflowTransitionDefinition(
            id=uuid.uuid4(),
            workflow_definition_id=wf_def_id,
            from_stage_code=from_code,
            to_stage_code=to_code,
            action_name=action,
            description=desc,
            required_role=role,
            required_permission=perm,
            requires_remarks=req_remarks,
        )
        wf_def.transitions.append(trans)

    return wf_def


@pytest.fixture
def central_user():
    return build_test_user(CENTRAL_USER_ID, "central_official", "CENTRAL_OFFICIAL")


@pytest.fixture
def state_user_ts():
    return build_test_user(STATE_TS_USER_ID, "state_ts", "STATE_OFFICIAL", state="Telangana")


@pytest.fixture
def district_user_hyd():
    return build_test_user(DISTRICT_HYD_USER_ID, "district_hyd", "DISTRICT_OFFICER", state="Telangana", district="Hyderabad")


@pytest.fixture
def citizen_user():
    return build_test_user(CITIZEN_USER_ID, "citizen_user", "CITIZEN")


@pytest.fixture
def mock_project_ts():
    proj = Project(
        id="NLA-TS-2026-001",
        name="Hyderabad Expressway Expansion",
        ministry="MORT&H",
        implementing_agency="NHAI",
        state="Telangana",
        district="Hyderabad",
        project_type="Highway",
        land_required=1250.0,
        land_acquired=0.0,
        progress=0.0,
        status="Active",
        lifecycle=[],
    )
    proj.parcels = []
    proj.created_at = "2026-09-23T00:00:00Z"
    proj.updated_at = "2026-09-23T00:00:00Z"
    return proj


@pytest.fixture
def mock_project_mh():
    proj = Project(
        id="NLA-MH-2026-004",
        name="DMIC Shendra-Bidkin Node",
        ministry="Ministry of Commerce",
        implementing_agency="NICDC",
        state="Maharashtra",
        district="Aurangabad",
        project_type="Industrial Corridor",
        land_required=3400.0,
        land_acquired=0.0,
        progress=0.0,
        status="Active",
        lifecycle=[],
    )
    proj.parcels = []
    proj.created_at = "2026-09-23T00:00:00Z"
    proj.updated_at = "2026-09-23T00:00:00Z"
    return proj


# ---------------------------------------------------------------------------
# Test Cases
# ---------------------------------------------------------------------------

async def test_get_workflow_status(client: AsyncClient, central_user: User, mock_project_ts: Project):
    """Test retrieving active workflow status and initial stage."""
    app.dependency_overrides[get_current_user] = lambda: central_user
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    wf_def = build_mock_workflow_definition()
    instance = WorkflowInstance(
        id=uuid.uuid4(),
        project_id="NLA-TS-2026-001",
        workflow_definition_id=wf_def.id,
        current_stage_code="PROJECT_PLANNING",
        status="ACTIVE",
        stage_started_at=datetime.now(timezone.utc),
        history=[],
    )
    instance.workflow_definition = wf_def

    with patch("app.repositories.project.ProjectRepository.get_by_id", AsyncMock(return_value=mock_project_ts)):
        with patch("app.repositories.workflow.WorkflowRepository.get_or_create_instance_for_project", AsyncMock(return_value=instance)):
            with patch("app.repositories.workflow.WorkflowRepository.get_allowed_transitions", AsyncMock(return_value=[wf_def.transitions[0]])):
                response = await client.get("/api/v1/workflows/projects/NLA-TS-2026-001")
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["project_id"] == "NLA-TS-2026-001"
                assert data["current_stage_code"] == "PROJECT_PLANNING"
                assert data["stage_order"] == 1
                assert data["total_stages"] == 14
                assert len(data["pending_actions"]) == 1
                assert data["pending_actions"][0]["action_name"] == "APPROVE_PLANNING"

    app.dependency_overrides.clear()


async def test_valid_transition_execution(client: AsyncClient, central_user: User, mock_project_ts: Project):
    """Test valid transition from PROJECT_PLANNING to LAND_REQUIREMENT advances stage and creates audit/history."""
    app.dependency_overrides[get_current_user] = lambda: central_user
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    wf_def = build_mock_workflow_definition()
    matching_transition = wf_def.transitions[0]  # APPROVE_PLANNING -> LAND_REQUIREMENT

    instance = WorkflowInstance(
        id=uuid.uuid4(),
        project_id="NLA-TS-2026-001",
        workflow_definition_id=wf_def.id,
        current_stage_code="PROJECT_PLANNING",
        status="ACTIVE",
        stage_started_at=datetime.now(timezone.utc),
        history=[],
    )
    instance.workflow_definition = wf_def

    payload = {
        "action_name": "APPROVE_PLANNING",
        "target_stage_code": "LAND_REQUIREMENT",
        "remarks": "Feasibility DPR approved by Ministry sanction committee",
    }

    with patch("app.repositories.project.ProjectRepository.get_by_id", AsyncMock(return_value=mock_project_ts)):
        with patch("app.repositories.workflow.WorkflowRepository.get_or_create_instance_for_project", AsyncMock(return_value=instance)):
            with patch("app.repositories.workflow.WorkflowRepository.find_matching_transition", AsyncMock(return_value=matching_transition)):
                with patch("app.repositories.workflow.WorkflowRepository.record_transition_history", AsyncMock()):
                    with patch("app.repositories.audit.AuditRepository.log_action", AsyncMock()):
                        with patch("app.repositories.audit.AuditRepository.create_notification", AsyncMock()):
                            with patch("app.repositories.workflow.WorkflowRepository.get_instance_by_project_id", AsyncMock(return_value=instance)):
                                with patch("app.repositories.workflow.WorkflowRepository.get_allowed_transitions", AsyncMock(return_value=[])):
                                    response = await client.post(
                                        "/api/v1/workflows/projects/NLA-TS-2026-001/transitions",
                                        json=payload,
                                    )
                                    assert response.status_code == status.HTTP_200_OK
                                    data = response.json()
                                    assert data["current_stage_code"] == "LAND_REQUIREMENT"
                                    assert data["stage_order"] == 2
                                    assert mock_project_ts.progress > 0.0

    app.dependency_overrides.clear()


async def test_invalid_transition_rejected(client: AsyncClient, central_user: User, mock_project_ts: Project):
    """Test that illegal transition attempting to skip stages is rejected with 422."""
    app.dependency_overrides[get_current_user] = lambda: central_user
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    wf_def = build_mock_workflow_definition()
    instance = WorkflowInstance(
        id=uuid.uuid4(),
        project_id="NLA-TS-2026-001",
        workflow_definition_id=wf_def.id,
        current_stage_code="PROJECT_PLANNING",
        status="ACTIVE",
        stage_started_at=datetime.now(timezone.utc),
    )
    instance.workflow_definition = wf_def

    # Illegal jump from PROJECT_PLANNING to COMPENSATION_ASSESSMENT
    illegal_payload = {
        "action_name": "SUBMIT_VALUATION",
        "target_stage_code": "COMPENSATION_ASSESSMENT",
        "remarks": "Illegal skip",
    }

    with patch("app.repositories.project.ProjectRepository.get_by_id", AsyncMock(return_value=mock_project_ts)):
        with patch("app.repositories.workflow.WorkflowRepository.get_or_create_instance_for_project", AsyncMock(return_value=instance)):
            with patch("app.repositories.workflow.WorkflowRepository.find_matching_transition", AsyncMock(return_value=None)):
                response = await client.post(
                    "/api/v1/workflows/projects/NLA-TS-2026-001/transitions",
                    json=illegal_payload,
                )
                assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
                data = response.json()
                assert "illegal transition" in data["message"].lower()

    app.dependency_overrides.clear()


async def test_unauthorized_role_transition_rejected(client: AsyncClient, citizen_user: User, mock_project_ts: Project):
    """Test that citizen role is rejected when attempting an administrative transition (403 Forbidden)."""
    app.dependency_overrides[get_current_user] = lambda: citizen_user
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    wf_def = build_mock_workflow_definition()
    transition_req_central = wf_def.transitions[0]  # Requires CENTRAL_OFFICIAL

    instance = WorkflowInstance(
        id=uuid.uuid4(),
        project_id="NLA-TS-2026-001",
        workflow_definition_id=wf_def.id,
        current_stage_code="PROJECT_PLANNING",
        status="ACTIVE",
        stage_started_at=datetime.now(timezone.utc),
    )
    instance.workflow_definition = wf_def

    payload = {
        "action_name": "APPROVE_PLANNING",
        "target_stage_code": "LAND_REQUIREMENT",
        "remarks": "Citizen attempt",
    }

    with patch("app.repositories.project.ProjectRepository.get_by_id", AsyncMock(return_value=mock_project_ts)):
        with patch("app.repositories.workflow.WorkflowRepository.get_or_create_instance_for_project", AsyncMock(return_value=instance)):
            with patch("app.repositories.workflow.WorkflowRepository.find_matching_transition", AsyncMock(return_value=transition_req_central)):
                response = await client.post(
                    "/api/v1/workflows/projects/NLA-TS-2026-001/transitions",
                    json=payload,
                )
                assert response.status_code == status.HTTP_403_FORBIDDEN
                data = response.json()
                assert "access denied" in data["message"].lower()

    app.dependency_overrides.clear()


async def test_geographic_scope_restriction_on_workflow(client: AsyncClient, state_user_ts: User, mock_project_mh: Project):
    """Test that State Official for Telangana is rejected when attempting transition on Maharashtra project (403)."""
    app.dependency_overrides[get_current_user] = lambda: state_user_ts
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("app.repositories.project.ProjectRepository.get_by_id", AsyncMock(return_value=mock_project_mh)):
        response = await client.get("/api/v1/workflows/projects/NLA-MH-2026-004")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert "jurisdiction" in data["message"].lower()

    app.dependency_overrides.clear()


async def test_mandatory_remarks_enforcement(client: AsyncClient, district_user_hyd: User, mock_project_ts: Project):
    """Test that transitions with requires_remarks=True fail if remarks are omitted."""
    app.dependency_overrides[get_current_user] = lambda: district_user_hyd
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    wf_def = build_mock_workflow_definition()
    # Transition requiring remarks: PUBLISH_NOTIFICATION (Sec 11)
    trans_with_remarks = next(t for t in wf_def.transitions if t.requires_remarks)

    instance = WorkflowInstance(
        id=uuid.uuid4(),
        project_id="NLA-TS-2026-001",
        workflow_definition_id=wf_def.id,
        current_stage_code=trans_with_remarks.from_stage_code,
        status="ACTIVE",
        stage_started_at=datetime.now(timezone.utc),
    )
    instance.workflow_definition = wf_def

    payload = {
        "action_name": trans_with_remarks.action_name,
        "target_stage_code": trans_with_remarks.to_stage_code,
        "remarks": "",  # Empty remarks!
    }

    with patch("app.repositories.project.ProjectRepository.get_by_id", AsyncMock(return_value=mock_project_ts)):
        with patch("app.repositories.workflow.WorkflowRepository.get_or_create_instance_for_project", AsyncMock(return_value=instance)):
            with patch("app.repositories.workflow.WorkflowRepository.find_matching_transition", AsyncMock(return_value=trans_with_remarks)):
                response = await client.post(
                    "/api/v1/workflows/projects/NLA-TS-2026-001/transitions",
                    json=payload,
                )
                assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
                data = response.json()
                assert "remarks are mandatory" in data["message"].lower()

    app.dependency_overrides.clear()


async def test_get_transition_history(client: AsyncClient, central_user: User, mock_project_ts: Project):
    """Test retrieving chronological transition history."""
    app.dependency_overrides[get_current_user] = lambda: central_user
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    wf_def = build_mock_workflow_definition()
    history_entry = WorkflowTransitionHistory(
        id=uuid.uuid4(),
        workflow_instance_id=uuid.uuid4(),
        from_stage_code="PROJECT_PLANNING",
        to_stage_code="LAND_REQUIREMENT",
        action="APPROVE_PLANNING",
        performed_by_name="Central Official",
        performed_by_role="CENTRAL_OFFICIAL",
        remarks="Approved feasibility",
        timestamp=datetime.now(timezone.utc),
    )

    instance = WorkflowInstance(
        id=uuid.uuid4(),
        project_id="NLA-TS-2026-001",
        workflow_definition_id=wf_def.id,
        current_stage_code="LAND_REQUIREMENT",
        status="ACTIVE",
        stage_started_at=datetime.now(timezone.utc),
        history=[history_entry],
    )
    instance.workflow_definition = wf_def

    with patch("app.repositories.project.ProjectRepository.get_by_id", AsyncMock(return_value=mock_project_ts)):
        with patch("app.repositories.workflow.WorkflowRepository.get_or_create_instance_for_project", AsyncMock(return_value=instance)):
            response = await client.get("/api/v1/workflows/projects/NLA-TS-2026-001/history")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 1
            assert data[0]["action"] == "APPROVE_PLANNING"
            assert data[0]["performed_by_name"] == "Central Official"

    app.dependency_overrides.clear()

