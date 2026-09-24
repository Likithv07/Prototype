import io
import uuid
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import status
from httpx import AsyncClient


def make_mock_session():
    s = AsyncMock()
    s.add = MagicMock()
    return s
from app.api.deps import get_current_user, get_db
from app.core.compensation_rules import get_default_statutory_rule
from app.core.security import hash_password
from app.main import app
from app.models.audit import Notification
from app.models.compensation import (
    Award,
    CompensationAssessment,
    CompensationRule,
)
from app.models.consent import LandownerConsent
from app.models.grievance import (
    Grievance,
    GrievanceDocument,
    GrievanceHistory,
)
from app.models.parcel import LandParcel
from app.models.project import Project
from app.models.rr import (
    AffectedFamily,
    ResettlementColony,
    RrBenefit,
    RrEligibility,
)
from app.models.user import Role, User

pytestmark = pytest.mark.asyncio

DISTRICT_OFFICER_ID = uuid.uuid4()
OTHER_DISTRICT_OFFICER_ID = uuid.uuid4()
FIELD_OFFICER_ID = uuid.uuid4()
OTHER_FIELD_OFFICER_ID = uuid.uuid4()
CITIZEN_RAJESH_ID = uuid.uuid4()
CITIZEN_SITA_ID = uuid.uuid4()


def build_test_user(
    user_id: uuid.UUID,
    username: str,
    role_name: str,
    state: str = "Telangana",
    district: str = "Hyderabad",
    aadhaar_last4: str = "1245",
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
        aadhaar_hash=f"SHA256-AADHAAR-MOCK-{aadhaar_last4}",
    )
    user.roles = [role]
    return user


@pytest.fixture
def district_officer_hyd():
    return build_test_user(DISTRICT_OFFICER_ID, "officer_hyd", "DISTRICT_OFFICER", "Telangana", "Hyderabad")


@pytest.fixture
def district_officer_wgl():
    return build_test_user(OTHER_DISTRICT_OFFICER_ID, "officer_wgl", "DISTRICT_OFFICER", "Telangana", "Warangal")


@pytest.fixture
def field_officer_hyd():
    return build_test_user(FIELD_OFFICER_ID, "officer_field_hyd", "FIELD_OFFICER", "Telangana", "Hyderabad")


@pytest.fixture
def field_officer_wgl():
    return build_test_user(OTHER_FIELD_OFFICER_ID, "officer_field_wgl", "FIELD_OFFICER", "Telangana", "Warangal")


@pytest.fixture
def citizen_rajesh():
    return build_test_user(CITIZEN_RAJESH_ID, "rajesh_kumar", "CITIZEN", "Telangana", "Hyderabad", "1245")


@pytest.fixture
def citizen_sita():
    return build_test_user(CITIZEN_SITA_ID, "sita_devi", "CITIZEN", "Telangana", "Hyderabad", "9811")


@pytest.fixture
def rajesh_parcel():
    parcel = LandParcel(
        id="TS-HYD-2026-001245",
        survey_number="145/2",
        project_id="NLA-TS-2026-001",
        landowner_name="Rajesh Kumar",
        masked_aadhaar="XXXX-XXXX-1245",
        masked_bank_account="SBI - •••• •••• 4892",
        state="Telangana",
        district="Hyderabad",
        village="Ghatkesar",
        area_acres=2.5,
        land_type="Agricultural",
        acquisition_status="Compensation Approved",
        compensation_status="Approved",
        possession_status="Demarcated",
        market_value_per_acre=1000000.0,
        multiplier_factor=1.5,
        asset_valuation=250000.0,
        total_compensation=8450000.0,
        consent_received=True,
        consent_date=date(2026, 3, 10),
        center_lat=17.4485,
        center_lng=78.6812,
        polygon_coords=[[17.448, 78.681], [17.449, 78.681], [17.449, 78.682], [17.448, 78.682]],
        owner_user_id=CITIZEN_RAJESH_ID,
        assigned_officer_id=FIELD_OFFICER_ID,
    )
    parcel.created_at = datetime.now(timezone.utc)
    parcel.updated_at = datetime.now(timezone.utc)
    return parcel


@pytest.fixture
def sita_parcel():
    parcel = LandParcel(
        id="TS-HYD-2026-001246",
        survey_number="146/1",
        project_id="NLA-TS-2026-001",
        landowner_name="Sita Devi",
        masked_aadhaar="XXXX-XXXX-9811",
        masked_bank_account="SBI - •••• •••• 9811",
        state="Telangana",
        district="Hyderabad",
        village="Ghatkesar",
        area_acres=1.8,
        land_type="Commercial",
        acquisition_status="Under Survey",
        compensation_status="Pending",
        possession_status="Not Started",
        market_value_per_acre=1200000.0,
        multiplier_factor=1.0,
        asset_valuation=100000.0,
        total_compensation=0.0,
        consent_received=False,
        consent_date=None,
        center_lat=17.4495,
        center_lng=78.6822,
        polygon_coords=[[17.449, 78.682], [17.450, 78.682], [17.450, 78.683], [17.449, 78.683]],
        owner_user_id=CITIZEN_SITA_ID,
        assigned_officer_id=OTHER_FIELD_OFFICER_ID,
    )
    parcel.created_at = datetime.now(timezone.utc)
    parcel.updated_at = datetime.now(timezone.utc)
    return parcel


@pytest.fixture
def mock_assessment(rajesh_parcel: LandParcel):
    rule = get_default_statutory_rule()
    award = Award(
        id="AWD-TS-HYD-2026-001245",
        assessment_id=f"COMP-{rajesh_parcel.id}",
        parcel_id=rajesh_parcel.id,
        project_id=rajesh_parcel.project_id,
        award_number="AWARD/CALA/HYD/2026/042",
        award_date=date(2026, 3, 15),
        competent_authority_id=DISTRICT_OFFICER_ID,
        competent_authority_name="District Collector Hyderabad",
        competent_authority_designation="Competent Authority Land Acquisition (CALA)",
        total_awarded_amount=8450000.0,
        digital_seal_ref="NIC-DSC-GOV-2026-9812",
        status="ISSUED",
    )
    award.created_at = datetime.now(timezone.utc)

    assessment = CompensationAssessment(
        id=f"COMP-{rajesh_parcel.id}",
        parcel_id=rajesh_parcel.id,
        project_id=rajesh_parcel.project_id,
        landowner_id=rajesh_parcel.owner_user_id,
        landowner_name=rajesh_parcel.landowner_name,
        survey_number=rajesh_parcel.survey_number,
        rule_id=rule.id,
        rule_version=rule.version,
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
        calculated_by_id=DISTRICT_OFFICER_ID,
    )
    assessment.created_at = datetime.now(timezone.utc)
    assessment.updated_at = datetime.now(timezone.utc)
    assessment.award = award
    assessment.components = []
    assessment.history = []
    return assessment


@pytest.fixture
def mock_consent(rajesh_parcel: LandParcel):
    consent = LandownerConsent(
        id=f"CONSENT-{rajesh_parcel.id}",
        parcel_id=rajesh_parcel.id,
        project_id=rajesh_parcel.project_id,
        landowner_user_id=rajesh_parcel.owner_user_id,
        landowner_name=rajesh_parcel.landowner_name,
        landowner_aadhaar_masked=rajesh_parcel.masked_aadhaar or "XXXX-XXXX-1245",
        consent_type="VOLUNTARY_ACQUISITION",
        status="VERIFIED",
        esign_verified=True,
        verified_at=datetime.now(timezone.utc),
        document_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    )
    consent.created_at = datetime.now(timezone.utc)
    consent.updated_at = datetime.now(timezone.utc)
    consent.parcel = rajesh_parcel
    consent.history = []
    return consent


@pytest.fixture
def rajesh_grievance(rajesh_parcel: LandParcel):
    g = Grievance(
        id="GRV-2026-TS-A1B2C3",
        parcel_id=rajesh_parcel.id,
        project_id=rajesh_parcel.project_id,
        citizen_user_id=CITIZEN_RAJESH_ID,
        citizen_name="Rajesh Kumar",
        citizen_phone="+91 98765 43210",
        category="Compensation Issue",
        subject="Clarification on Solatium percentage for Borewell",
        description="Requesting confirmation that borewell asset valuation includes electric pump set replacement grant.",
        status="SUBMITTED",
        priority="NORMAL",
    )
    g.created_at = datetime.now(timezone.utc)
    g.updated_at = datetime.now(timezone.utc)
    g.parcel = rajesh_parcel
    g.documents = []
    g.history = []
    return g


@pytest.fixture
def sita_grievance(sita_parcel: LandParcel):
    g = Grievance(
        id="GRV-2026-TS-S1T2A3",
        parcel_id=sita_parcel.id,
        project_id=sita_parcel.project_id,
        citizen_user_id=CITIZEN_SITA_ID,
        citizen_name="Sita Devi",
        citizen_phone="+91 98450 11223",
        category="Ownership Issue",
        subject="Survey boundary encroachment objection",
        description="Boundary stone misplaced during demarcation.",
        status="SUBMITTED",
        priority="NORMAL",
    )
    g.created_at = datetime.now(timezone.utc)
    g.updated_at = datetime.now(timezone.utc)
    g.parcel = sita_parcel
    g.documents = []
    g.history = []
    return g


@pytest.fixture
def rajesh_affected_family(rajesh_parcel: LandParcel):
    fam = AffectedFamily(
        id="FAM-TS-001",
        project_id=rajesh_parcel.project_id,
        parcel_id=rajesh_parcel.id,
        citizen_user_id=CITIZEN_RAJESH_ID,
        head_of_family="Rajesh Kumar & Family",
        aadhaar_masked="XXXX-XXXX-1245",
        contact_number="+91 98765 43210",
        state="Telangana",
        district="Hyderabad",
        village="Ghatkesar",
        family_members_count=5,
        affected_type="Agricultural",
        relocation_status="Rehabilitated",
        total_financial_package_lakhs=72.25,
        status="Active",
    )
    fam.created_at = datetime.now(timezone.utc)
    fam.updated_at = datetime.now(timezone.utc)
    fam.eligibility = RrEligibility(
        id=uuid.uuid4(),
        family_id=fam.id,
        is_eligible=True,
        eligibility_criteria="RFCTLARR Second Schedule - Agricultural Land Loser",
        status="VERIFIED",
        verification_date=date(2026, 2, 20),
    )
    fam.eligibility.created_at = datetime.now(timezone.utc)
    benefit = RrBenefit(
        id=uuid.uuid4(),
        family_id=fam.id,
        benefit_type="LIVELIHOOD_GRANT",
        description="One-time livelihood grant for agriculture diversification",
        monetary_value_lakhs=5.0,
        benefit_status="SANCTIONED",
        disbursement_status="DISBURSED",
        disbursed_amount_lakhs=5.0,
        disbursement_date=date(2026, 3, 1),
        disbursement_ref="PFMS-RR-TS-2026-9912",
    )
    benefit.created_at = datetime.now(timezone.utc)
    fam.benefits = [benefit]
    fam.parcel = rajesh_parcel
    return fam


# =============================================================================
# 1. Citizen Parcel Access & Scoped Data Isolation Tests
# =============================================================================

async def test_citizen_can_access_own_parcels(
    client: AsyncClient,
    citizen_rajesh: User,
    rajesh_parcel: LandParcel,
):
    """Citizen can retrieve all parcels registered under their ownership."""
    app.dependency_overrides[get_current_user] = lambda: citizen_rajesh
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    with patch("app.repositories.parcel.ParcelRepository.list_parcels", AsyncMock(return_value=[rajesh_parcel])):
        resp = await client.get("/api/v1/citizen/parcels")
        assert resp.status_code == status.HTTP_200_OK, resp.text
        data = resp.json()
        assert len(data) == 1
        assert data[0]["id"] == rajesh_parcel.id
        assert data[0]["landowner_name"] == "Rajesh Kumar"
        assert data[0]["area_acres"] == 2.5
        assert len(data[0]["polygon_coords"]) == 4


async def test_citizen_data_isolation_cannot_access_other_parcel(
    client: AsyncClient,
    citizen_sita: User,
    rajesh_parcel: LandParcel,
):
    """Citizen Sita attempting to retrieve Citizen Rajesh's parcel is rejected with 403 Forbidden."""
    app.dependency_overrides[get_current_user] = lambda: citizen_sita
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    with patch("app.repositories.parcel.ParcelRepository.get_by_id", AsyncMock(return_value=rajesh_parcel)):
        resp = await client.get(f"/api/v1/citizen/parcels/{rajesh_parcel.id}")
        assert resp.status_code == status.HTTP_403_FORBIDDEN


# =============================================================================
# 2. Citizen Compensation Tracking & Award Verification
# =============================================================================

async def test_citizen_can_track_compensation_award(
    client: AsyncClient,
    citizen_rajesh: User,
    rajesh_parcel: LandParcel,
    mock_assessment: CompensationAssessment,
):
    """Citizen reads statutory valuation, 100% Solatium, 12% interest, and Section 31 award seal."""
    app.dependency_overrides[get_current_user] = lambda: citizen_rajesh
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    with patch("app.repositories.parcel.ParcelRepository.get_by_id", AsyncMock(return_value=rajesh_parcel)):
        with patch("app.repositories.compensation.CompensationRepository.get_assessment_by_parcel_id", AsyncMock(return_value=mock_assessment)):
            resp = await client.get(f"/api/v1/citizen/compensation/{rajesh_parcel.id}")
            assert resp.status_code == status.HTTP_200_OK, resp.text
            data = resp.json()

            assert data["parcel_id"] == rajesh_parcel.id
            assert data["basic_land_value"] == 2500000.0
            assert data["solatium_amount"] == 4000000.0
            assert data["interest_amount"] == 450000.0
            assert data["total_compensation"] == 8450000.0
            assert data["status"] == "APPROVED"
            assert data["award_number"] == "AWARD/CALA/HYD/2026/042"
            assert data["digital_seal_ref"] == "NIC-DSC-GOV-2026-9812"


async def test_citizen_compensation_isolation_forbidden(
    client: AsyncClient,
    citizen_sita: User,
    rajesh_parcel: LandParcel,
):
    """Citizen Sita cannot track compensation for Citizen Rajesh's parcel."""
    app.dependency_overrides[get_current_user] = lambda: citizen_sita
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    with patch("app.repositories.parcel.ParcelRepository.get_by_id", AsyncMock(return_value=rajesh_parcel)):
        resp = await client.get(f"/api/v1/citizen/compensation/{rajesh_parcel.id}")
        assert resp.status_code == status.HTTP_403_FORBIDDEN


# =============================================================================
# 3. Citizen Consent Status & Aadhaar eSign Simulation
# =============================================================================

async def test_citizen_consent_status_and_esign(
    client: AsyncClient,
    citizen_rajesh: User,
    rajesh_parcel: LandParcel,
    mock_consent: LandownerConsent,
):
    """Citizen retrieves consent status and can execute simulated Aadhaar eSign."""
    app.dependency_overrides[get_current_user] = lambda: citizen_rajesh
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    with patch("app.repositories.parcel.ParcelRepository.get_by_id", AsyncMock(return_value=rajesh_parcel)):
        with patch("app.repositories.consent.ConsentRepository.get_by_parcel_id", AsyncMock(return_value=mock_consent)):
            resp = await client.get(f"/api/v1/citizen/consent/{rajesh_parcel.id}")
            assert resp.status_code == status.HTTP_200_OK, resp.text
            data = resp.json()
            assert data["consent_received"] is True
            assert data["status"] == "VERIFIED"
            assert data["is_esign_completed"] is True


async def test_citizen_execute_esign(
    client: AsyncClient,
    citizen_rajesh: User,
    rajesh_parcel: LandParcel,
    mock_consent: LandownerConsent,
):
    """Executing Aadhaar eSign simulation updates consent verification status."""
    app.dependency_overrides[get_current_user] = lambda: citizen_rajesh
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    with patch("app.services.consent.ConsentService.submit_consent", AsyncMock(return_value=mock_consent)):
        resp = await client.post(f"/api/v1/citizen/consent/{rajesh_parcel.id}/esign")
        assert resp.status_code == status.HTTP_200_OK, resp.text
        data = resp.json()
        assert data["parcel_id"] == rajesh_parcel.id
        assert data["is_esign_completed"] is True


# =============================================================================
# 4. Citizen Payment & DBT Disbursement Tracking
# =============================================================================

async def test_citizen_payment_status(
    client: AsyncClient,
    citizen_rajesh: User,
    rajesh_parcel: LandParcel,
    mock_assessment: CompensationAssessment,
):
    """Citizen retrieves PFMS mandate ID, DBT transfer route, and bank account mask."""
    app.dependency_overrides[get_current_user] = lambda: citizen_rajesh
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    with patch("app.repositories.parcel.ParcelRepository.get_by_id", AsyncMock(return_value=rajesh_parcel)):
        with patch("app.repositories.compensation.CompensationRepository.get_assessment_by_parcel_id", AsyncMock(return_value=mock_assessment)):
            resp = await client.get(f"/api/v1/citizen/payment/{rajesh_parcel.id}")
            assert resp.status_code == status.HTTP_200_OK, resp.text
            data = resp.json()

            assert data["total_award_amount"] == 8450000.0
            assert data["disbursement_route"] == "Direct Benefit Transfer (DBT)"
            assert "SBI" in data["masked_bank_account"]
            assert data["payment_status"] == "READY_FOR_PFMS_TRANSFER"
            assert "PFMS-GOI-2026-" in data["pfms_mandate_id"]


# =============================================================================
# 5. Statutory Grievance Lifecycle & Scoping Tests
# =============================================================================

async def test_citizen_lodge_grievance(
    client: AsyncClient,
    citizen_rajesh: User,
    rajesh_parcel: LandParcel,
    rajesh_grievance: Grievance,
):
    """Citizen lodges a grievance petition on their parcel successfully."""
    app.dependency_overrides[get_current_user] = lambda: citizen_rajesh
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    with patch("app.repositories.parcel.ParcelRepository.get_by_id", AsyncMock(return_value=rajesh_parcel)):
        with patch("app.repositories.grievance.GrievanceRepository.create_grievance", AsyncMock(return_value=rajesh_grievance)):
            with patch("app.repositories.grievance.GrievanceRepository.add_history", AsyncMock()):
                with patch("app.repositories.grievance.GrievanceRepository.get_by_id", AsyncMock(return_value=rajesh_grievance)):
                    with patch("app.repositories.audit.AuditRepository.log_action", AsyncMock()):
                        with patch("app.repositories.audit.AuditRepository.create_notification", AsyncMock()):
                            payload = {
                                "parcel_id": rajesh_parcel.id,
                                "citizen_name": "Rajesh Kumar",
                                "citizen_phone": "+91 98765 43210",
                                "category": "Compensation Issue",
                                "subject": "Clarification on Solatium percentage for Borewell",
                                "description": "Requesting confirmation that borewell asset valuation includes electric pump set replacement grant.",
                                "priority": "NORMAL",
                            }
                            resp = await client.post("/api/v1/citizen/grievances", json=payload)
                            assert resp.status_code == status.HTTP_201_CREATED, resp.text
                            data = resp.json()
                            assert data["id"] == rajesh_grievance.id
                            assert data["status"] == "SUBMITTED"


async def test_citizen_cannot_lodge_grievance_on_other_parcel(
    client: AsyncClient,
    citizen_sita: User,
    rajesh_parcel: LandParcel,
):
    """Citizen Sita cannot lodge a grievance on Citizen Rajesh's parcel."""
    app.dependency_overrides[get_current_user] = lambda: citizen_sita
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    with patch("app.repositories.parcel.ParcelRepository.get_by_id", AsyncMock(return_value=rajesh_parcel)):
        payload = {
            "parcel_id": rajesh_parcel.id,
            "citizen_name": "Sita Devi",
            "citizen_phone": "+91 98450 11223",
            "category": "Land Area Dispute",
            "subject": "Unauthorized access attempt",
            "description": "Attempting to dispute Rajesh's parcel.",
            "priority": "NORMAL",
        }
        resp = await client.post("/api/v1/citizen/grievances", json=payload)
        assert resp.status_code == status.HTTP_403_FORBIDDEN


async def test_district_officer_geographic_isolation(
    client: AsyncClient,
    district_officer_wgl: User,
    rajesh_grievance: Grievance,
):
    """Officer in Warangal cannot access a grievance filed in Hyderabad."""
    app.dependency_overrides[get_current_user] = lambda: district_officer_wgl
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    with patch("app.repositories.grievance.GrievanceRepository.get_by_id", AsyncMock(return_value=rajesh_grievance)):
        resp = await client.get(f"/api/v1/grievances/{rajesh_grievance.id}")
        assert resp.status_code == status.HTTP_403_FORBIDDEN


async def test_officer_grievance_lifecycle_assign_and_resolve(
    client: AsyncClient,
    district_officer_hyd: User,
    rajesh_grievance: Grievance,
):
    """District Officer assigns, updates status, and resolves grievance with formal hearing findings."""
    app.dependency_overrides[get_current_user] = lambda: district_officer_hyd
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    with patch("app.repositories.grievance.GrievanceRepository.get_by_id", AsyncMock(return_value=rajesh_grievance)):
        with patch("app.repositories.user.UserRepository.get_by_id", AsyncMock(return_value=district_officer_hyd)):
            with patch("app.repositories.grievance.GrievanceRepository.add_history", AsyncMock()):
                with patch("app.repositories.audit.AuditRepository.create_notification", AsyncMock()):
                    # 1. Assign
                    assign_resp = await client.post(
                        f"/api/v1/grievances/{rajesh_grievance.id}/assign",
                        json={"assigned_officer_id": str(district_officer_hyd.id), "notes": "Assigned for joint hearing."},
                    )
                    assert assign_resp.status_code == status.HTTP_200_OK, assign_resp.text
                    assert rajesh_grievance.status == "OFFICER_ASSIGNED"

                    # 2. Status Update
                    status_resp = await client.put(
                        f"/api/v1/grievances/{rajesh_grievance.id}/status",
                        json={"status": "UNDER_REVIEW", "notes": "Revenue records verified."},
                    )
                    assert status_resp.status_code == status.HTTP_200_OK, status_resp.text
                    assert rajesh_grievance.status == "UNDER_REVIEW"

                    # 3. Resolve
                    resolve_resp = await client.post(
                        f"/api/v1/grievances/{rajesh_grievance.id}/resolve",
                        json={"resolution_notes": "Borewell replacement grant confirmed and incorporated into final award."},
                    )
                    assert resolve_resp.status_code == status.HTTP_200_OK, resolve_resp.text
                    assert rajesh_grievance.status == "RESOLVED"
                    assert "confirmed and incorporated" in rajesh_grievance.resolution_notes


async def test_grievance_document_attachment(
    client: AsyncClient,
    citizen_rajesh: User,
    rajesh_grievance: Grievance,
):
    """Attaching a supporting title deed or affidavit to a grievance petition."""
    app.dependency_overrides[get_current_user] = lambda: citizen_rajesh
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    mock_doc = GrievanceDocument(
        id=uuid.uuid4(),
        grievance_id=rajesh_grievance.id,
        document_name="Title_Deed_Pahani.pdf",
        file_path="grievances/Title_Deed_Pahani.pdf",
        file_size_bytes=1024,
        mime_type="application/pdf",
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        uploaded_by_name="Rajesh Kumar",
        uploaded_at=datetime.now(timezone.utc),
    )

    with patch("app.repositories.grievance.GrievanceRepository.get_by_id", AsyncMock(return_value=rajesh_grievance)):
        with patch("app.repositories.grievance.GrievanceRepository.add_document", AsyncMock(return_value=mock_doc)):
            with patch("app.repositories.grievance.GrievanceRepository.add_history", AsyncMock()):
                files = {"file": ("Title_Deed_Pahani.pdf", io.BytesIO(b"%PDF-1.4 test document"), "application/pdf")}
                resp = await client.post(f"/api/v1/grievances/{rajesh_grievance.id}/documents", files=files)
                assert resp.status_code == status.HTTP_201_CREATED, resp.text
                data = resp.json()
                assert data["document_name"] == "Title_Deed_Pahani.pdf"


# =============================================================================
# 6. Rehabilitation & Resettlement (R&R) Scoping Tests
# =============================================================================

async def test_citizen_track_rr_entitlements(
    client: AsyncClient,
    citizen_rajesh: User,
    rajesh_affected_family: AffectedFamily,
):
    """Citizen Rajesh retrieves Second Schedule R&R entitlement package and disbursed livelihood grant."""
    app.dependency_overrides[get_current_user] = lambda: citizen_rajesh
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    with patch("app.repositories.rr.RrRepository.get_family_by_citizen_user_id", AsyncMock(return_value=rajesh_affected_family)):
        resp = await client.get("/api/v1/citizen/rr-benefits")
        assert resp.status_code == status.HTTP_200_OK, resp.text
        data = resp.json()

        assert data["id"] == "FAM-TS-001"
        assert data["family_members_count"] == 5
        assert data["eligibility"]["status"] == "VERIFIED"
        assert len(data["benefits"]) == 1
        assert data["benefits"][0]["benefit_type"] == "LIVELIHOOD_GRANT"
        assert data["benefits"][0]["disbursement_status"] == "DISBURSED"
        assert data["benefits"][0]["monetary_value_lakhs"] == 5.0


async def test_officer_disburse_rr_benefit(
    client: AsyncClient,
    district_officer_hyd: User,
    rajesh_affected_family: AffectedFamily,
):
    """District Officer disburses R&R benefit under PFMS reference."""
    app.dependency_overrides[get_current_user] = lambda: district_officer_hyd
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    benefit = rajesh_affected_family.benefits[0]
    benefit.disbursement_status = "PENDING"
    benefit.disbursed_amount_lakhs = 0.0
    with patch("app.repositories.rr.RrRepository.get_benefit_by_id", AsyncMock(return_value=benefit)):
        with patch("app.repositories.audit.AuditRepository.create_notification", AsyncMock()):
            payload = {
                "disbursed_amount_lakhs": 5.0,
                "disbursement_ref": "PFMS-RR-TS-2026-9912",
                "remarks": "Subsistence grant disbursed to beneficiary account.",
            }
            resp = await client.post(f"/api/v1/rr/benefits/{benefit.id}/disburse", json=payload)
            assert resp.status_code == status.HTTP_200_OK, resp.text
            data = resp.json()
            assert data["disbursement_status"] == "DISBURSED"
            assert data["disbursement_ref"] == "PFMS-RR-TS-2026-9912"


# =============================================================================
# 7. Citizen Notifications Tests
# =============================================================================

async def test_citizen_notifications(
    client: AsyncClient,
    citizen_rajesh: User,
):
    """Citizen retrieves notifications and marks them as read."""
    app.dependency_overrides[get_current_user] = lambda: citizen_rajesh
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    notif_id = uuid.uuid4()
    mock_notif = Notification(
        id=notif_id,
        user_id=CITIZEN_RAJESH_ID,
        title="Compensation Award Digitally Sealed",
        message="Section 31 statutory award has been digitally sealed by CALA Hyderabad.",
        category="compensation",
        link_view="citizen_compensation",
        is_read=False,
    )
    mock_notif.created_at = datetime.now(timezone.utc)

    with patch("app.repositories.audit.AuditRepository.list_user_notifications", AsyncMock(return_value=[mock_notif])):
        resp = await client.get("/api/v1/citizen/notifications")
        assert resp.status_code == status.HTTP_200_OK, resp.text
        data = resp.json()
        assert len(data) == 1
        assert data[0]["title"] == "Compensation Award Digitally Sealed"
        assert data[0]["is_read"] is False

    with patch("app.repositories.audit.AuditRepository.mark_notification_as_read", AsyncMock(return_value=mock_notif)):
        put_resp = await client.put(f"/api/v1/citizen/notifications/{notif_id}/read")
        assert put_resp.status_code == status.HTTP_200_OK, put_resp.text
        put_data = put_resp.json()
        assert put_data["id"] == str(notif_id)


# =============================================================================
# 8. Negative IDOR Authorization Tests (Prompt 11 Review Fixes)
# =============================================================================

async def test_citizen_cannot_access_other_citizen_grievance(
    client: AsyncClient,
    citizen_sita: User,
    rajesh_grievance: Grievance,
):
    """Citizen Sita attempting to read Citizen Rajesh's grievance is rejected with 403 Forbidden."""
    app.dependency_overrides[get_current_user] = lambda: citizen_sita
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    with patch("app.repositories.grievance.GrievanceRepository.get_by_id", AsyncMock(return_value=rajesh_grievance)):
        resp = await client.get(f"/api/v1/citizen/grievances/{rajesh_grievance.id}")
        assert resp.status_code == status.HTTP_403_FORBIDDEN


async def test_citizen_cannot_access_other_citizen_rr(
    client: AsyncClient,
    citizen_sita: User,
    rajesh_affected_family: AffectedFamily,
):
    """Citizen Sita attempting to retrieve Citizen Rajesh's R&R family details is rejected with 403 Forbidden."""
    app.dependency_overrides[get_current_user] = lambda: citizen_sita
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    with patch("app.repositories.rr.RrRepository.get_family_by_id", AsyncMock(return_value=rajesh_affected_family)):
        resp = await client.get(f"/api/v1/rr/families/{rajesh_affected_family.id}")
        assert resp.status_code == status.HTTP_403_FORBIDDEN


async def test_citizen_cannot_access_other_citizen_payment(
    client: AsyncClient,
    citizen_sita: User,
    rajesh_parcel: LandParcel,
):
    """Citizen Sita attempting to read payment details of Citizen Rajesh's parcel is rejected with 403 Forbidden."""
    app.dependency_overrides[get_current_user] = lambda: citizen_sita
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    with patch("app.repositories.parcel.ParcelRepository.get_by_id", AsyncMock(return_value=rajesh_parcel)):
        resp = await client.get(f"/api/v1/citizen/payment/{rajesh_parcel.id}")
        assert resp.status_code == status.HTTP_403_FORBIDDEN


async def test_citizen_cannot_mark_other_citizen_notification_read(
    client: AsyncClient,
    citizen_sita: User,
):
    """Citizen Sita cannot acknowledge or read another citizen's notification."""
    app.dependency_overrides[get_current_user] = lambda: citizen_sita
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    other_notif_id = uuid.uuid4()
    with patch("app.repositories.audit.AuditRepository.mark_notification_as_read", AsyncMock(return_value=None)):
        resp = await client.put(f"/api/v1/citizen/notifications/{other_notif_id}/read")
        assert resp.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# 9. Administrative Role Restrictions on Citizen (RBAC Protection)
# =============================================================================

async def test_citizen_cannot_assign_grievance(
    client: AsyncClient,
    citizen_rajesh: User,
    rajesh_grievance: Grievance,
):
    """Citizen attempting to allocate an inquiry officer on a grievance is blocked with 403."""
    app.dependency_overrides[get_current_user] = lambda: citizen_rajesh
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    payload = {"assigned_officer_id": str(DISTRICT_OFFICER_ID), "notes": "Citizen trying to assign"}
    resp = await client.post(f"/api/v1/grievances/{rajesh_grievance.id}/assign", json=payload)
    assert resp.status_code == status.HTTP_403_FORBIDDEN


async def test_citizen_cannot_update_grievance_status(
    client: AsyncClient,
    citizen_rajesh: User,
    rajesh_grievance: Grievance,
):
    """Citizen attempting to arbitrarily update grievance lifecycle status is blocked with 403."""
    app.dependency_overrides[get_current_user] = lambda: citizen_rajesh
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    payload = {"status": "RESOLVED", "notes": "Citizen marking self as resolved"}
    resp = await client.put(f"/api/v1/grievances/{rajesh_grievance.id}/status", json=payload)
    assert resp.status_code == status.HTTP_403_FORBIDDEN


async def test_citizen_cannot_resolve_grievance(
    client: AsyncClient,
    citizen_rajesh: User,
    rajesh_grievance: Grievance,
):
    """Citizen attempting to record official inquiry findings is blocked with 403."""
    app.dependency_overrides[get_current_user] = lambda: citizen_rajesh
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    payload = {"resolution_notes": "Citizen trying to record resolution"}
    resp = await client.post(f"/api/v1/grievances/{rajesh_grievance.id}/resolve", json=payload)
    assert resp.status_code == status.HTTP_403_FORBIDDEN


async def test_citizen_cannot_create_rr_family(
    client: AsyncClient,
    citizen_rajesh: User,
):
    """Citizen attempting to create an affected family administrative record is blocked with 403."""
    app.dependency_overrides[get_current_user] = lambda: citizen_rajesh
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    payload = {
        "id": "FAM-ILLEGAL-01",
        "project_id": "NLA-TS-2026-001",
        "head_of_family": "Rajesh Kumar",
        "state": "Telangana",
        "district": "Hyderabad",
        "village": "Ghatkesar",
    }
    resp = await client.post("/api/v1/rr/families", json=payload)
    assert resp.status_code == status.HTTP_403_FORBIDDEN


async def test_citizen_cannot_disburse_rr_benefit(
    client: AsyncClient,
    citizen_rajesh: User,
    rajesh_affected_family: AffectedFamily,
):
    """Citizen attempting to disburse an R&R benefit grant is blocked with 403."""
    app.dependency_overrides[get_current_user] = lambda: citizen_rajesh
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    benefit = rajesh_affected_family.benefits[0]
    payload = {
        "disbursed_amount_lakhs": 5.0,
        "disbursement_ref": "ILLEGAL-REF",
    }
    resp = await client.post(f"/api/v1/rr/benefits/{benefit.id}/disburse", json=payload)
    assert resp.status_code == status.HTTP_403_FORBIDDEN


# =============================================================================
# 10. Field Officer Grievance Scoping Tests
# =============================================================================

async def test_field_officer_access_assigned_parcel_grievance(
    client: AsyncClient,
    field_officer_hyd: User,
    rajesh_grievance: Grievance,
):
    """Field Officer can access grievance associated with a parcel assigned to them."""
    app.dependency_overrides[get_current_user] = lambda: field_officer_hyd
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    with patch("app.repositories.grievance.GrievanceRepository.get_by_id", AsyncMock(return_value=rajesh_grievance)):
        resp = await client.get(f"/api/v1/grievances/{rajesh_grievance.id}")
        assert resp.status_code == status.HTTP_200_OK, resp.text
        data = resp.json()
        assert data["id"] == rajesh_grievance.id


async def test_field_officer_forbidden_unassigned_parcel_grievance(
    client: AsyncClient,
    field_officer_hyd: User,
    sita_grievance: Grievance,
):
    """Field Officer attempting to access grievance on a parcel NOT assigned to them is rejected with 403."""
    app.dependency_overrides[get_current_user] = lambda: field_officer_hyd
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    with patch("app.repositories.grievance.GrievanceRepository.get_by_id", AsyncMock(return_value=sita_grievance)):
        resp = await client.get(f"/api/v1/grievances/{sita_grievance.id}")
        assert resp.status_code == status.HTTP_403_FORBIDDEN


async def test_field_officer_list_scoped_to_assigned_parcels(
    client: AsyncClient,
    field_officer_hyd: User,
    rajesh_grievance: Grievance,
):
    """Field Officer listing grievances passes assigned_officer_id and returns only assigned grievances."""
    app.dependency_overrides[get_current_user] = lambda: field_officer_hyd
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    mock_list = AsyncMock(return_value=[rajesh_grievance])
    with patch("app.repositories.grievance.GrievanceRepository.list_grievances", mock_list):
        resp = await client.get("/api/v1/grievances")
        assert resp.status_code == status.HTTP_200_OK, resp.text
        data = resp.json()
        assert len(data) == 1
        assert data[0]["id"] == rajesh_grievance.id

        # Verify assigned_officer_id was passed to repository query
        _, kwargs = mock_list.call_args
        assert kwargs["assigned_officer_id"] == field_officer_hyd.id


# =============================================================================
# 11. Grievance State Machine Tests
# =============================================================================

async def test_grievance_invalid_backward_transition(
    client: AsyncClient,
    district_officer_hyd: User,
    rajesh_grievance: Grievance,
):
    """Grievance in UNDER_REVIEW cannot transition backwards to OFFICER_ASSIGNED (422)."""
    app.dependency_overrides[get_current_user] = lambda: district_officer_hyd
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    rajesh_grievance.status = "UNDER_REVIEW"
    with patch("app.repositories.grievance.GrievanceRepository.get_by_id", AsyncMock(return_value=rajesh_grievance)):
        resp = await client.put(
            f"/api/v1/grievances/{rajesh_grievance.id}/status",
            json={"status": "OFFICER_ASSIGNED", "notes": "Illegal backwards transition"},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, resp.text
        data = resp.json()
        assert "illegal status transition" in data["message"].lower()


async def test_grievance_skipping_required_stages(
    client: AsyncClient,
    district_officer_hyd: User,
    rajesh_grievance: Grievance,
):
    """Grievance in SUBMITTED cannot skip required stages to directly resolve (422)."""
    app.dependency_overrides[get_current_user] = lambda: district_officer_hyd
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    rajesh_grievance.status = "SUBMITTED"
    with patch("app.repositories.grievance.GrievanceRepository.get_by_id", AsyncMock(return_value=rajesh_grievance)):
        resp = await client.post(
            f"/api/v1/grievances/{rajesh_grievance.id}/resolve",
            json={"resolution_notes": "Skipping to resolution prematurely"},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, resp.text
        data = resp.json()
        assert "must be in 'under_review' stage" in data["message"].lower()


async def test_grievance_terminal_state_modification_rejected(
    client: AsyncClient,
    district_officer_hyd: User,
    rajesh_grievance: Grievance,
):
    """Grievance in RESOLVED terminal state cannot be re-opened, re-assigned, or modified (422)."""
    app.dependency_overrides[get_current_user] = lambda: district_officer_hyd
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    rajesh_grievance.status = "RESOLVED"
    with patch("app.repositories.grievance.GrievanceRepository.get_by_id", AsyncMock(return_value=rajesh_grievance)):
        # 1. Reject status modification
        resp1 = await client.put(
            f"/api/v1/grievances/{rajesh_grievance.id}/status",
            json={"status": "UNDER_REVIEW", "notes": "Reopening"},
        )
        assert resp1.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, resp1.text
        assert "terminal state" in resp1.json()["message"].lower()

        # 2. Reject assignment
        resp2 = await client.post(
            f"/api/v1/grievances/{rajesh_grievance.id}/assign",
            json={"assigned_officer_id": str(DISTRICT_OFFICER_ID), "notes": "Reassigning terminal"},
        )
        assert resp2.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, resp2.text
        assert "terminal state" in resp2.json()["message"].lower()

        # 3. Reject re-resolution
        resp3 = await client.post(
            f"/api/v1/grievances/{rajesh_grievance.id}/resolve",
            json={"resolution_notes": "Resolving already resolved"},
        )
        assert resp3.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, resp3.text
        assert "terminal state" in resp3.json()["message"].lower()


async def test_grievance_invalid_status_value_rejected(
    client: AsyncClient,
    district_officer_hyd: User,
    rajesh_grievance: Grievance,
):
    """Passing an arbitrary or unsupported status value is rejected (422)."""
    app.dependency_overrides[get_current_user] = lambda: district_officer_hyd
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    rajesh_grievance.status = "SUBMITTED"
    with patch("app.repositories.grievance.GrievanceRepository.get_by_id", AsyncMock(return_value=rajesh_grievance)):
        resp = await client.put(
            f"/api/v1/grievances/{rajesh_grievance.id}/status",
            json={"status": "CLOSED_ARBITRARY", "notes": "Unsupported status"},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, resp.text
        data = resp.json()
        assert "invalid grievance status" in data["message"].lower()


# =============================================================================
# 12. R&R Benefit Integrity Tests
# =============================================================================

async def test_rr_benefit_cannot_be_disbursed_twice(
    client: AsyncClient,
    district_officer_hyd: User,
    rajesh_affected_family: AffectedFamily,
):
    """Disbursing an already DISBURSED benefit is rejected with 422 Unprocessable Entity."""
    app.dependency_overrides[get_current_user] = lambda: district_officer_hyd
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    benefit = rajesh_affected_family.benefits[0]
    benefit.disbursement_status = "DISBURSED"

    with patch("app.repositories.rr.RrRepository.get_benefit_by_id", AsyncMock(return_value=benefit)):
        payload = {
            "disbursed_amount_lakhs": 5.0,
            "disbursement_ref": "SECOND-DISBURSE-ATTEMPT",
        }
        resp = await client.post(f"/api/v1/rr/benefits/{benefit.id}/disburse", json=payload)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, resp.text
        assert "already been disbursed" in resp.json()["message"].lower()


async def test_rr_benefit_cannot_disburse_more_than_sanctioned(
    client: AsyncClient,
    district_officer_hyd: User,
    rajesh_affected_family: AffectedFamily,
):
    """Disbursing an amount greater than the sanctioned monetary value is rejected with 422."""
    app.dependency_overrides[get_current_user] = lambda: district_officer_hyd
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    benefit = rajesh_affected_family.benefits[0]
    benefit.disbursement_status = "PENDING"
    benefit.monetary_value_lakhs = 5.0

    with patch("app.repositories.rr.RrRepository.get_benefit_by_id", AsyncMock(return_value=benefit)):
        payload = {
            "disbursed_amount_lakhs": 15.0,  # Exceeds 5.0 Lakhs
            "disbursement_ref": "EXCESS-DISBURSE-REF",
        }
        resp = await client.post(f"/api/v1/rr/benefits/{benefit.id}/disburse", json=payload)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, resp.text
        assert "cannot exceed sanctioned monetary value" in resp.json()["message"].lower()


# =============================================================================
# 13. Centralized Audit Logging Tests
# =============================================================================

async def test_centralized_audit_logging_on_grievance_and_rr(
    client: AsyncClient,
    district_officer_hyd: User,
    rajesh_grievance: Grievance,
    rajesh_affected_family: AffectedFamily,
):
    """Verify centralized audit logging is invoked on grievance assignment, status update, resolution, and R&R."""
    app.dependency_overrides[get_current_user] = lambda: district_officer_hyd
    app.dependency_overrides[get_db] = lambda: make_mock_session()

    mock_audit = AsyncMock()

    # 1. Grievance Assignment
    rajesh_grievance.status = "SUBMITTED"
    with patch("app.repositories.grievance.GrievanceRepository.get_by_id", AsyncMock(return_value=rajesh_grievance)):
        with patch("app.repositories.user.UserRepository.get_by_id", AsyncMock(return_value=district_officer_hyd)):
            with patch("app.repositories.grievance.GrievanceRepository.add_history", AsyncMock()):
                with patch("app.repositories.audit.AuditRepository.create_notification", AsyncMock()):
                    with patch("app.repositories.audit.AuditRepository.log_action", mock_audit):
                        await client.post(
                            f"/api/v1/grievances/{rajesh_grievance.id}/assign",
                            json={"assigned_officer_id": str(district_officer_hyd.id), "notes": "Hearing officer assigned"},
                        )
                        mock_audit.assert_called()
                        _, kwargs = mock_audit.call_args
                        assert kwargs["action"] == "GRIEVANCE_ASSIGNED"
                        assert kwargs["entity_id"] == rajesh_grievance.id

    # 2. Grievance Status Update
    mock_audit.reset_mock()
    rajesh_grievance.status = "OFFICER_ASSIGNED"
    with patch("app.repositories.grievance.GrievanceRepository.get_by_id", AsyncMock(return_value=rajesh_grievance)):
        with patch("app.repositories.grievance.GrievanceRepository.add_history", AsyncMock()):
            with patch("app.repositories.audit.AuditRepository.create_notification", AsyncMock()):
                with patch("app.repositories.audit.AuditRepository.log_action", mock_audit):
                    await client.put(
                        f"/api/v1/grievances/{rajesh_grievance.id}/status",
                        json={"status": "UNDER_REVIEW", "notes": "Under official inquiry"},
                    )
                    mock_audit.assert_called()
                    _, kwargs = mock_audit.call_args
                    assert kwargs["action"] == "GRIEVANCE_STATUS_UPDATED"

    # 3. Grievance Resolution
    mock_audit.reset_mock()
    rajesh_grievance.status = "UNDER_REVIEW"
    with patch("app.repositories.grievance.GrievanceRepository.get_by_id", AsyncMock(return_value=rajesh_grievance)):
        with patch("app.repositories.grievance.GrievanceRepository.add_history", AsyncMock()):
            with patch("app.repositories.audit.AuditRepository.create_notification", AsyncMock()):
                with patch("app.repositories.audit.AuditRepository.log_action", mock_audit):
                    await client.post(
                        f"/api/v1/grievances/{rajesh_grievance.id}/resolve",
                        json={"resolution_notes": "Verified and resolved favorably."},
                    )
                    mock_audit.assert_called()
                    _, kwargs = mock_audit.call_args
                    assert kwargs["action"] == "GRIEVANCE_RESOLVED"

    # 4. R&R Benefit Disbursement
    mock_audit.reset_mock()
    benefit = rajesh_affected_family.benefits[0]
    benefit.disbursement_status = "PENDING"
    benefit.benefit_status = "SANCTIONED"
    benefit.monetary_value_lakhs = 5.0
    with patch("app.repositories.rr.RrRepository.get_benefit_by_id", AsyncMock(return_value=benefit)):
        with patch("app.repositories.audit.AuditRepository.create_notification", AsyncMock()):
            with patch("app.repositories.audit.AuditRepository.log_action", mock_audit):
                await client.post(
                    f"/api/v1/rr/benefits/{benefit.id}/disburse",
                    json={"disbursed_amount_lakhs": 5.0, "disbursement_ref": "AUDIT-TEST-REF-99"},
                )
                mock_audit.assert_called()
                _, kwargs = mock_audit.call_args
                assert kwargs["action"] == "DISBURSE_RR_BENEFIT"

