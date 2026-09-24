import uuid
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import status
from httpx import AsyncClient
from app.api.deps import get_current_user, get_db
from app.core.compensation_rules import get_default_statutory_rule
from app.core.security import hash_password
from app.main import app
from app.models.compensation import (
    Award,
    CompensationAssessment,
    CompensationComponent,
    CompensationHistory,
    CompensationRule,
)
from app.models.document import Document
from app.models.field import FieldPhoto, FieldSurveyRecord
from app.models.parcel import LandParcel
from app.models.project import Project
from app.models.user import Role, User
from app.models.workflow import WorkflowInstance, WorkflowStageDefinition

pytestmark = pytest.mark.asyncio

DISTRICT_OFFICER_ID = uuid.uuid4()
CITIZEN_ID = uuid.uuid4()


def build_test_user(
    user_id: uuid.UUID,
    username: str,
    role_name: str,
    state: str = "Telangana",
    district: str = "Hyderabad",
) -> User:
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


@pytest.fixture
def district_officer():
    return build_test_user(DISTRICT_OFFICER_ID, "district_collector", "DISTRICT_OFFICER")


@pytest.fixture
def citizen_user():
    return build_test_user(CITIZEN_ID, "citizen_rajesh", "CITIZEN")


@pytest.fixture
def mock_parcel():
    parcel = LandParcel(
        id="TS-HYD-2026-001245",
        survey_number="145/2",
        project_id="NLA-TS-2026-001",
        landowner_name="Rajesh Kumar",
        masked_aadhaar="XXXX-XXXX-1245",
        state="Telangana",
        district="Hyderabad",
        village="Ghatkesar",
        area_acres=2.5,
        land_type="Agricultural",
        acquisition_status="Under Verification",
        compensation_status="Pending",
        possession_status="Not Started",
        market_value_per_acre=1000000.0,
        multiplier_factor=1.5,
        asset_valuation=250000.0,
        owner_user_id=CITIZEN_ID,
    )
    parcel.created_at = datetime.now(timezone.utc)
    parcel.updated_at = datetime.now(timezone.utc)
    return parcel


@pytest.fixture
def mock_project():
    proj = Project(
        id="NLA-TS-2026-001",
        name="Hyderabad Outer Ring Railway Corridor",
        ministry="Ministry of Railways",
        implementing_agency="South Central Railway",
        project_type="Railway",
        state="Telangana",
        district="Hyderabad",
        status="Under Survey",
    )
    proj.created_at = datetime.now(timezone.utc)
    proj.updated_at = datetime.now(timezone.utc)
    return proj


@pytest.fixture
def default_rule():
    return get_default_statutory_rule()


# ===========================================================================
# 1. Statutory Calculator Tests (Sections 26-30 RFCTLARR Act 2013)
# ===========================================================================

async def test_statutory_calculator_rfctlarr_formula(
    client: AsyncClient,
    district_officer: User,
    mock_parcel: LandParcel,
    default_rule: CompensationRule,
):
    """Test interactive calculator accurately implements RFCTLARR Section 26-30 formula.
    
    Calculation:
    - Basic Land Value = 2.5 acres * 1,000,000 = 2,500,000
    - Multiplied Land Value = 2,500,000 * 1.5 = 3,750,000
    - Market Value + Assets = 3,750,000 + 250,000 = 4,000,000
    - Solatium (100%) = 4,000,000 * 1.0 = 4,000,000
    - Additional Interest (12%) = 3,750,000 * 0.12 = 450,000
    - Total Compensation = 4,000,000 + 4,000,000 + 450,000 = 8,450,000
    """
    app.dependency_overrides[get_current_user] = lambda: district_officer
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("app.repositories.parcel.ParcelRepository.get_by_id", AsyncMock(return_value=mock_parcel)):
        with patch("app.repositories.compensation.CompensationRepository.get_active_rule", AsyncMock(return_value=default_rule)):
            payload = {
                "land_area_acres": 2.5,
                "market_value_per_acre": 1000000.0,
                "multiplier_factor": 1.5,
                "asset_valuation": 250000.0,
                "solatium_percentage": 100.0,
                "interest_percentage": 12.0,
            }
            resp = await client.post(f"/api/v1/compensation/{mock_parcel.id}/calculate", json=payload)
            assert resp.status_code == status.HTTP_200_OK, resp.text
            data = resp.json()

            assert data["basic_land_value"] == 2500000.0
            assert data["multiplied_land_value"] == 3750000.0
            assert data["market_value_plus_assets"] == 4000000.0
            assert data["solatium_amount"] == 4000000.0
            assert data["interest_amount"] == 450000.0
            assert data["total_compensation"] == 8450000.0
            assert data["rule_id"] == default_rule.id


# ===========================================================================
# 2. Assessment Creation, Updating & Itemized Components
# ===========================================================================

async def test_get_or_create_draft_assessment(
    client: AsyncClient,
    district_officer: User,
    mock_parcel: LandParcel,
    default_rule: CompensationRule,
):
    """Test retrieving an assessment for a parcel creates an initial draft from parcel data if not existing."""
    app.dependency_overrides[get_current_user] = lambda: district_officer
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    now = datetime.now(timezone.utc)
    mock_assessment = CompensationAssessment(
        id=f"COMP-{mock_parcel.id}",
        parcel_id=mock_parcel.id,
        project_id=mock_parcel.project_id,
        landowner_id=CITIZEN_ID,
        landowner_name=mock_parcel.landowner_name,
        survey_number=mock_parcel.survey_number,
        rule_id=default_rule.id,
        rule_version="v1.0",
        status="DRAFT",
        land_area_acres=2.5,
        market_value_per_acre=1000000.0,
        multiplier_factor=1.5,
        asset_valuation=250000.0,
        basic_land_value=2500000.0,
        multiplied_land_value=3750000.0,
        market_value_plus_assets=4000000.0,
        solatium_percentage=100.0,
        solatium_amount=4000000.0,
        interest_percentage=12.0,
        interest_amount=450000.0,
        total_compensation=8450000.0,
        calculated_by_id=district_officer.id,
    )
    mock_assessment.created_at = now
    mock_assessment.updated_at = now
    mock_assessment.parcel = mock_parcel

    with patch("app.repositories.parcel.ParcelRepository.get_by_id", AsyncMock(return_value=mock_parcel)):
        with patch("app.repositories.compensation.CompensationRepository.get_assessment_by_parcel_id", AsyncMock(side_effect=[None, mock_assessment])):
            with patch("app.repositories.compensation.CompensationRepository.get_active_rule", AsyncMock(return_value=default_rule)):
                with patch("app.repositories.compensation.CompensationRepository.create_assessment", AsyncMock(return_value=mock_assessment)):
                    with patch("app.repositories.compensation.CompensationRepository.add_history", AsyncMock()):
                        with patch("app.repositories.compensation.CompensationRepository.get_assessment_by_id", AsyncMock(return_value=mock_assessment)):
                            resp = await client.get(f"/api/v1/compensation/{mock_parcel.id}")
                            assert resp.status_code == status.HTTP_200_OK, resp.text
                            data = resp.json()
                            assert data["id"] == f"COMP-{mock_parcel.id}"
                            assert data["status"] == "DRAFT"
                            assert data["total_compensation"] == 8450000.0


async def test_update_assessment_and_submit(
    client: AsyncClient,
    district_officer: User,
    mock_parcel: LandParcel,
    default_rule: CompensationRule,
):
    """Test updating assessment parameters and submitting for supervisory review."""
    app.dependency_overrides[get_current_user] = lambda: district_officer
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    now = datetime.now(timezone.utc)
    assessment_id = f"COMP-{mock_parcel.id}"

    mock_assessment = CompensationAssessment(
        id=assessment_id,
        parcel_id=mock_parcel.id,
        project_id=mock_parcel.project_id,
        landowner_name=mock_parcel.landowner_name,
        survey_number=mock_parcel.survey_number,
        rule_id=default_rule.id,
        rule_version="v1.0",
        status="DRAFT",
        land_area_acres=2.5,
        market_value_per_acre=1000000.0,
        multiplier_factor=1.5,
        asset_valuation=250000.0,
        basic_land_value=2500000.0,
        multiplied_land_value=3750000.0,
        market_value_plus_assets=4000000.0,
        solatium_percentage=100.0,
        solatium_amount=4000000.0,
        interest_percentage=12.0,
        interest_amount=450000.0,
        total_compensation=8450000.0,
        calculated_by_id=district_officer.id,
    )
    mock_assessment.created_at = now
    mock_assessment.updated_at = now
    mock_assessment.parcel = mock_parcel

    submitted_assessment = CompensationAssessment(
        id=assessment_id,
        parcel_id=mock_parcel.id,
        project_id=mock_parcel.project_id,
        landowner_name=mock_parcel.landowner_name,
        survey_number=mock_parcel.survey_number,
        rule_id=default_rule.id,
        rule_version="v1.0",
        status="SUBMITTED",
        land_area_acres=2.5,
        market_value_per_acre=1000000.0,
        multiplier_factor=1.5,
        asset_valuation=250000.0,
        basic_land_value=2500000.0,
        multiplied_land_value=3750000.0,
        market_value_plus_assets=4000000.0,
        solatium_percentage=100.0,
        solatium_amount=4000000.0,
        interest_percentage=12.0,
        interest_amount=450000.0,
        total_compensation=8450000.0,
        calculated_by_id=district_officer.id,
        submitted_by_id=district_officer.id,
        submitted_at=now,
    )
    submitted_assessment.created_at = now
    submitted_assessment.updated_at = now
    submitted_assessment.parcel = mock_parcel

    with patch("app.repositories.compensation.CompensationRepository.get_assessment_by_id", AsyncMock(side_effect=[mock_assessment, submitted_assessment])):
        with patch("app.repositories.compensation.CompensationRepository.update_assessment", AsyncMock(return_value=submitted_assessment)):
            with patch("app.repositories.compensation.CompensationRepository.add_history", AsyncMock()):
                with patch("app.repositories.audit.AuditRepository.log_action", AsyncMock()):
                    resp = await client.post(f"/api/v1/compensation/{assessment_id}/submit")
                    assert resp.status_code == status.HTTP_200_OK, resp.text
                    assert resp.json()["status"] == "SUBMITTED"


# ===========================================================================
# 3. Multi-Gated Approval Validation Tests
# ===========================================================================

async def test_approval_gate_citizen_forbidden(client: AsyncClient, citizen_user: User):
    """Test citizens cannot approve or reject compensation awards (Gate 1)."""
    app.dependency_overrides[get_current_user] = lambda: citizen_user
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    resp = await client.post(
        "/api/v1/compensation/COMP-TEST-001/approve",
        json={"digital_signature_consent": True, "digital_seal_ref": "NIC-DSC-GOV-2026-9812"},
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


async def test_approval_gate_missing_evidence_rejected(
    client: AsyncClient,
    district_officer: User,
    mock_parcel: LandParcel,
    default_rule: CompensationRule,
):
    """Test approval fails if parcel has no verified field survey evidence (Gate 3)."""
    app.dependency_overrides[get_current_user] = lambda: district_officer
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    now = datetime.now(timezone.utc)
    mock_assessment = CompensationAssessment(
        id=f"COMP-{mock_parcel.id}",
        parcel_id=mock_parcel.id,
        project_id=mock_parcel.project_id,
        landowner_name=mock_parcel.landowner_name,
        survey_number=mock_parcel.survey_number,
        rule_id=default_rule.id,
        rule_version="v1.0",
        status="SUBMITTED",
        land_area_acres=2.5,
        market_value_per_acre=1000000.0,
        multiplier_factor=1.5,
        asset_valuation=250000.0,
        basic_land_value=2500000.0,
        multiplied_land_value=3750000.0,
        market_value_plus_assets=4000000.0,
        solatium_percentage=100.0,
        solatium_amount=4000000.0,
        interest_percentage=12.0,
        interest_amount=450000.0,
        total_compensation=8450000.0,
        calculated_by_id=district_officer.id,
    )
    mock_assessment.created_at = now
    mock_assessment.updated_at = now
    mock_assessment.parcel = mock_parcel

    mock_db.add = MagicMock()

    # Mock DB execution returning empty lists for verified photos and surveys
    mock_result_empty = MagicMock()
    mock_result_empty.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(return_value=mock_result_empty)

    with patch("app.repositories.compensation.CompensationRepository.get_assessment_by_id", AsyncMock(return_value=mock_assessment)):
        with patch("app.repositories.parcel.ParcelRepository.get_by_id", AsyncMock(return_value=mock_parcel)):
            resp = await client.post(
                f"/api/v1/compensation/{mock_assessment.id}/approve",
                json={"digital_signature_consent": True, "digital_seal_ref": "NIC-DSC-GOV-2026-9812"},
            )
            assert resp.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY], resp.text
            assert "Gate 3 Violation" in resp.json()["detail"]


async def test_successful_award_approval_and_sync(
    client: AsyncClient,
    district_officer: User,
    mock_parcel: LandParcel,
    mock_project: Project,
    default_rule: CompensationRule,
):
    """Test full approval when all 6 statutory verification gates are met.
    
    Generates Section 31 statutory Award, updates parcel compensation status,
    records audit log, and creates in-app notification.
    """
    app.dependency_overrides[get_current_user] = lambda: district_officer
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    now = datetime.now(timezone.utc)
    assessment_id = f"COMP-{mock_parcel.id}"

    mock_assessment = CompensationAssessment(
        id=assessment_id,
        parcel_id=mock_parcel.id,
        project_id=mock_parcel.project_id,
        landowner_id=CITIZEN_ID,
        landowner_name=mock_parcel.landowner_name,
        survey_number=mock_parcel.survey_number,
        rule_id=default_rule.id,
        rule_version="v1.0",
        status="SUBMITTED",
        land_area_acres=2.5,
        market_value_per_acre=1000000.0,
        multiplier_factor=1.5,
        asset_valuation=250000.0,
        basic_land_value=2500000.0,
        multiplied_land_value=3750000.0,
        market_value_plus_assets=4000000.0,
        solatium_percentage=100.0,
        solatium_amount=4000000.0,
        interest_percentage=12.0,
        interest_amount=450000.0,
        total_compensation=8450000.0,
        calculated_by_id=district_officer.id,
    )
    mock_assessment.created_at = now
    mock_assessment.updated_at = now
    mock_assessment.parcel = mock_parcel

    mock_award = Award(
        id=f"AWARD-{mock_parcel.id}",
        assessment_id=assessment_id,
        parcel_id=mock_parcel.id,
        project_id=mock_parcel.project_id,
        award_number="LAO/HYD/2026/AW-145-2",
        award_date=date.today(),
        competent_authority_id=district_officer.id,
        competent_authority_name=district_officer.full_name,
        competent_authority_designation="DISTRICT_OFFICER",
        total_awarded_amount=8450000.0,
        digital_seal_ref="NIC-DSC-GOV-2026-9812",
        status="ISSUED",
    )
    mock_award.created_at = now
    mock_award.updated_at = now

    approved_assessment = CompensationAssessment(
        id=assessment_id,
        parcel_id=mock_parcel.id,
        project_id=mock_parcel.project_id,
        landowner_id=CITIZEN_ID,
        landowner_name=mock_parcel.landowner_name,
        survey_number=mock_parcel.survey_number,
        rule_id=default_rule.id,
        rule_version="v1.0",
        status="APPROVED",
        land_area_acres=2.5,
        market_value_per_acre=1000000.0,
        multiplier_factor=1.5,
        asset_valuation=250000.0,
        basic_land_value=2500000.0,
        multiplied_land_value=3750000.0,
        market_value_plus_assets=4000000.0,
        solatium_percentage=100.0,
        solatium_amount=4000000.0,
        interest_percentage=12.0,
        interest_amount=450000.0,
        total_compensation=8450000.0,
        calculated_by_id=district_officer.id,
        approved_by_id=district_officer.id,
        approved_at=now,
        digital_signature_ref="NIC-DSC-GOV-2026-9812",
    )
    approved_assessment.created_at = now
    approved_assessment.updated_at = now
    approved_assessment.parcel = mock_parcel
    approved_assessment.award = mock_award

    # Mock verified photo, verified doc, and workflow instance
    mock_photo = FieldPhoto(id="PH-1", parcel_id=mock_parcel.id, status="Verified")
    mock_doc = Document(id="DOC-1", parcel_id=mock_parcel.id, is_verified=True)
    mock_stage = WorkflowStageDefinition(id=uuid.uuid4(), stage_code="compensation", name="Compensation Formulation", stage_order=8)
    mock_wf = WorkflowInstance(id=uuid.uuid4(), project_id=mock_project.id, current_stage=mock_stage)

    mock_db.add = MagicMock()

    # Return items for DB query executions
    res_photo = MagicMock()
    res_photo.scalars.return_value.all.return_value = [mock_photo]

    res_survey = MagicMock()
    res_survey.scalars.return_value.all.return_value = []

    res_doc = MagicMock()
    res_doc.scalars.return_value.all.return_value = [mock_doc]

    res_wf = MagicMock()
    res_wf.scalars.return_value.first.return_value = mock_wf

    mock_db.execute = AsyncMock(side_effect=[res_photo, res_survey, res_doc, res_wf])

    with patch("app.repositories.compensation.CompensationRepository.get_assessment_by_id", AsyncMock(side_effect=[mock_assessment, approved_assessment])):
        with patch("app.repositories.parcel.ParcelRepository.get_by_id", AsyncMock(return_value=mock_parcel)):
            with patch("app.repositories.compensation.CompensationRepository.update_assessment", AsyncMock(return_value=approved_assessment)):
                with patch("app.repositories.compensation.CompensationRepository.create_award", AsyncMock(return_value=mock_award)):
                    with patch("app.repositories.parcel.ParcelRepository.update", AsyncMock(return_value=mock_parcel)):
                        with patch("app.repositories.compensation.CompensationRepository.add_history", AsyncMock()):
                            with patch("app.repositories.audit.AuditRepository.log_action", AsyncMock()):
                                with patch("app.repositories.audit.AuditRepository.create_notification", AsyncMock()):
                                    resp = await client.post(
                                        f"/api/v1/compensation/{assessment_id}/approve",
                                        json={
                                            "digital_signature_consent": True,
                                            "digital_seal_ref": "NIC-DSC-GOV-2026-9812",
                                            "approval_remarks": "Award certified under Section 31",
                                        },
                                    )
                                    assert resp.status_code == status.HTTP_200_OK, resp.text
                                    data = resp.json()
                                    assert data["status"] == "APPROVED"
                                    assert data["digital_signature_ref"] == "NIC-DSC-GOV-2026-9812"
                                    assert data["award"] is not None
                                    assert data["award"]["award_number"].startswith("LAO/")
                                    assert data["award"]["status"] == "ISSUED"


async def test_revision_request_flow(
    client: AsyncClient,
    district_officer: User,
    mock_parcel: LandParcel,
    default_rule: CompensationRule,
):
    """Test supervisor requesting revision with mandatory statutory grounds."""
    app.dependency_overrides[get_current_user] = lambda: district_officer
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    now = datetime.now(timezone.utc)
    assessment_id = f"COMP-{mock_parcel.id}"

    mock_assessment = CompensationAssessment(
        id=assessment_id,
        parcel_id=mock_parcel.id,
        project_id=mock_parcel.project_id,
        landowner_name=mock_parcel.landowner_name,
        survey_number=mock_parcel.survey_number,
        rule_id=default_rule.id,
        rule_version="v1.0",
        status="SUBMITTED",
        land_area_acres=2.5,
        market_value_per_acre=1000000.0,
        multiplier_factor=1.5,
        asset_valuation=250000.0,
        basic_land_value=2500000.0,
        multiplied_land_value=3750000.0,
        market_value_plus_assets=4000000.0,
        solatium_percentage=100.0,
        solatium_amount=4000000.0,
        interest_percentage=12.0,
        interest_amount=450000.0,
        total_compensation=8450000.0,
        calculated_by_id=district_officer.id,
    )
    mock_assessment.created_at = now
    mock_assessment.updated_at = now
    mock_assessment.parcel = mock_parcel

    revised_assessment = CompensationAssessment(
        id=assessment_id,
        parcel_id=mock_parcel.id,
        project_id=mock_parcel.project_id,
        landowner_name=mock_parcel.landowner_name,
        survey_number=mock_parcel.survey_number,
        rule_id=default_rule.id,
        rule_version="v1.0",
        status="REVISION_REQUESTED",
        land_area_acres=2.5,
        market_value_per_acre=1000000.0,
        multiplier_factor=1.5,
        asset_valuation=250000.0,
        basic_land_value=2500000.0,
        multiplied_land_value=3750000.0,
        market_value_plus_assets=4000000.0,
        solatium_percentage=100.0,
        solatium_amount=4000000.0,
        interest_percentage=12.0,
        interest_amount=450000.0,
        total_compensation=8450000.0,
        calculated_by_id=district_officer.id,
        revision_notes="Borewell valuation requires revised PWD certificate",
    )
    revised_assessment.created_at = now
    revised_assessment.updated_at = now
    revised_assessment.parcel = mock_parcel

    with patch("app.repositories.compensation.CompensationRepository.get_assessment_by_id", AsyncMock(side_effect=[mock_assessment, revised_assessment])):
        with patch("app.repositories.compensation.CompensationRepository.update_assessment", AsyncMock(return_value=revised_assessment)):
            with patch("app.repositories.compensation.CompensationRepository.add_history", AsyncMock()):
                with patch("app.repositories.audit.AuditRepository.log_action", AsyncMock()):
                    resp = await client.post(
                        f"/api/v1/compensation/{assessment_id}/reject",
                        json={"revision_notes": "Borewell valuation requires revised PWD certificate"},
                    )
                    assert resp.status_code == status.HTTP_200_OK, resp.text
                    assert resp.json()["status"] == "REVISION_REQUESTED"
                    assert resp.json()["revision_notes"] == "Borewell valuation requires revised PWD certificate"

