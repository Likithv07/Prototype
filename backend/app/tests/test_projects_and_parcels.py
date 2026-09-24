import uuid
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import status
from httpx import AsyncClient
from app.api.deps import get_current_user, get_db
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.parcel import LandParcel
from app.models.project import Project
from app.models.user import Role, User

pytestmark = pytest.mark.asyncio

# Test UUIDs
ADMIN_ID = uuid.uuid4()
CENTRAL_OFFICIAL_ID = uuid.uuid4()
STATE_OFFICIAL_TS_ID = uuid.uuid4()
DISTRICT_OFFICER_HYD_ID = uuid.uuid4()
FIELD_OFFICER_ID = uuid.uuid4()
CITIZEN_1_ID = uuid.uuid4()
CITIZEN_2_ID = uuid.uuid4()


def build_mock_user(user_id: uuid.UUID, username: str, role_name: str, state: str = None, district: str = None) -> User:
    """Helper to construct mock User model with assigned role and scope."""
    role = Role(id=uuid.uuid4(), name=role_name, is_system_role=True)
    user = User(
        id=user_id,
        email=f"{username}@bhoomi.gov.in",
        username=username,
        hashed_password=hash_password("Password123!"),
        full_name=f"{username.title()} User",
        is_active=True,
        is_verified=True,
        state=state,
        district=district,
    )
    user.roles = [role]
    return user


@pytest.fixture
def admin_user():
    return build_mock_user(ADMIN_ID, "admin_user", "ADMIN")


@pytest.fixture
def central_user():
    return build_mock_user(CENTRAL_OFFICIAL_ID, "central_official", "CENTRAL_OFFICIAL")


@pytest.fixture
def state_user_ts():
    return build_mock_user(STATE_OFFICIAL_TS_ID, "state_ts", "STATE_OFFICIAL", state="Telangana")


@pytest.fixture
def district_user_hyd():
    return build_mock_user(DISTRICT_OFFICER_HYD_ID, "district_hyd", "DISTRICT_OFFICER", state="Telangana", district="Hyderabad")


@pytest.fixture
def field_officer():
    return build_mock_user(FIELD_OFFICER_ID, "field_agent", "FIELD_OFFICER", state="Telangana", district="Hyderabad")


@pytest.fixture
def citizen_1():
    return build_mock_user(CITIZEN_1_ID, "citizen_rajesh", "CITIZEN", state="Telangana", district="Hyderabad")


@pytest.fixture
def citizen_2():
    return build_mock_user(CITIZEN_2_ID, "citizen_sita", "CITIZEN", state="Maharashtra", district="Pune")


# ---------------------------------------------------------------------------
# Project Tests
# ---------------------------------------------------------------------------

async def test_create_project_as_central_official(client: AsyncClient, central_user: User):
    """Verify Central Official can create a national project."""
    app.dependency_overrides[get_current_user] = lambda: central_user

    project_payload = {
        "id": "NLA-TS-2026-001",
        "name": "Hyderabad–Vijayawada Expressway (NH-65)",
        "ministry": "Ministry of Road Transport & Highways",
        "implementing_agency": "NHAI",
        "state": "Telangana",
        "district": "Hyderabad",
        "project_type": "Highway",
        "land_required": 1250.0,
        "land_acquired": 820.0,
        "progress": 65.0,
        "status": "Active",
        "budget_cr": 4850.0,
        "compensation_disbursed_cr": 614.2,
        "lifecycle": [
            {"id": 1, "name": "Proposal Submitted", "description": "DPR approved", "status": "Completed"}
        ],
    }

    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("app.repositories.project.ProjectRepository.get_by_id", AsyncMock(return_value=None)):
        with patch("app.repositories.project.ProjectRepository.create") as mock_create:
            created_mock = Project(**project_payload)
            created_mock.created_at = "2026-09-23T00:00:00Z"
            created_mock.updated_at = "2026-09-23T00:00:00Z"
            created_mock.parcels = []
            mock_create.return_value = created_mock

            response = await client.post("/api/v1/projects", json=project_payload)
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["id"] == "NLA-TS-2026-001"
            assert data["name"] == project_payload["name"]
            assert data["progress"] == 65.0

    app.dependency_overrides.clear()


async def test_create_project_role_rejection_for_citizen(client: AsyncClient, citizen_1: User):
    """Verify Citizen cannot create projects (403 Forbidden)."""
    app.dependency_overrides[get_current_user] = lambda: citizen_1

    response = await client.post(
        "/api/v1/projects",
        json={"id": "PROJ-FAIL", "name": "Forbidden Project", "ministry": "M", "implementing_agency": "I", "state": "S", "district": "D", "project_type": "Highway"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    app.dependency_overrides.clear()


async def test_state_official_geographic_scope_restriction(client: AsyncClient, state_user_ts: User):
    """Verify State Official for Telangana is rejected when attempting to view a Maharashtra project (403 Forbidden)."""
    app.dependency_overrides[get_current_user] = lambda: state_user_ts
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    # Project in Maharashtra
    mh_project = Project(
        id="NLA-MH-2026-004",
        name="DMIC Shendra-Bidkin Node",
        ministry="Ministry of Commerce",
        implementing_agency="NICDC",
        state="Maharashtra",
        district="Aurangabad",
        project_type="Industrial Corridor",
        land_required=3400.0,
        land_acquired=2890.0,
        progress=85.0,
        status="Possession",
        budget_cr=7200.0,
        compensation_disbursed_cr=2150.5,
        lifecycle=[],
    )
    mh_project.parcels = []
    mh_project.created_at = "2026-09-23T00:00:00Z"
    mh_project.updated_at = "2026-09-23T00:00:00Z"

    with patch("app.repositories.project.ProjectRepository.get_by_id", AsyncMock(return_value=mh_project)):
        response = await client.get("/api/v1/projects/NLA-MH-2026-004")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert "jurisdiction" in data["message"].lower()

    app.dependency_overrides.clear()


async def test_central_official_national_scope_bypass(client: AsyncClient, central_user: User):
    """Verify Central Official can access projects in any state."""
    app.dependency_overrides[get_current_user] = lambda: central_user
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    mh_project = Project(
        id="NLA-MH-2026-004",
        name="DMIC Shendra-Bidkin Node",
        ministry="Ministry of Commerce",
        implementing_agency="NICDC",
        state="Maharashtra",
        district="Aurangabad",
        project_type="Industrial Corridor",
        land_required=3400.0,
        land_acquired=2890.0,
        progress=85.0,
        status="Possession",
        budget_cr=7200.0,
        compensation_disbursed_cr=2150.5,
        lifecycle=[],
    )
    mh_project.parcels = []
    mh_project.created_at = "2026-09-23T00:00:00Z"
    mh_project.updated_at = "2026-09-23T00:00:00Z"

    with patch("app.repositories.project.ProjectRepository.get_by_id", AsyncMock(return_value=mh_project)):
        response = await client.get("/api/v1/projects/NLA-MH-2026-004")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == "NLA-MH-2026-004"
        assert data["state"] == "Maharashtra"

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Land Parcel Tests & PostGIS GeoJSON
# ---------------------------------------------------------------------------

async def test_create_parcel_with_geojson(client: AsyncClient, district_user_hyd: User):
    """Verify parcel creation with PostGIS GeoJSON Polygon input."""
    app.dependency_overrides[get_current_user] = lambda: district_user_hyd
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    parent_project = Project(
        id="NLA-TS-2026-001",
        name="Hyderabad Expressway",
        ministry="MORT&H",
        implementing_agency="NHAI",
        state="Telangana",
        district="Hyderabad",
        project_type="Highway",
        land_required=100.0,
        land_acquired=50.0,
        progress=50.0,
        status="Active",
        budget_cr=100.0,
        compensation_disbursed_cr=10.0,
    )

    parcel_payload = {
        "id": "TS-HYD-2026-001245",
        "survey_number": "145/2",
        "project_id": "NLA-TS-2026-001",
        "landowner_name": "Rajesh Kumar",
        "landowner_mobile": "+91 98765 43210",
        "landowner_address": "Ghatkesar, Hyderabad",
        "masked_aadhaar": "XXXX-XXXX-8921",
        "masked_bank_account": "HDFC - •••• 4192",
        "state": "Telangana",
        "district": "Hyderabad",
        "village": "Ghatkesar",
        "area_acres": 2.5,
        "land_type": "Agricultural",
        "acquisition_status": "Compensation Pending",
        "compensation_status": "Pending",
        "possession_status": "Demarcated",
        "market_value_per_acre": 2500000.0,
        "total_compensation": 7225000.0,
        "geojson": {
            "type": "Polygon",
            "coordinates": [
                [
                    [78.681, 17.442],
                    [78.685, 17.442],
                    [78.685, 17.446],
                    [78.681, 17.446],
                    [78.681, 17.442],
                ]
            ],
        },
    }

    mock_parcel = LandParcel(
        id=parcel_payload["id"],
        survey_number=parcel_payload["survey_number"],
        project_id=parcel_payload["project_id"],
        landowner_name=parcel_payload["landowner_name"],
        state=parcel_payload["state"],
        district=parcel_payload["district"],
        village=parcel_payload["village"],
        area_acres=parcel_payload["area_acres"],
        land_type=parcel_payload["land_type"],
        acquisition_status=parcel_payload["acquisition_status"],
        compensation_status=parcel_payload["compensation_status"],
        possession_status=parcel_payload["possession_status"],
        market_value_per_acre=parcel_payload["market_value_per_acre"],
        total_compensation=parcel_payload["total_compensation"],
        center_lat=17.444,
        center_lng=78.683,
        owner_user_id=CITIZEN_1_ID,
        assigned_officer_id=FIELD_OFFICER_ID,
    )
    mock_parcel.created_at = "2026-09-23T00:00:00Z"
    mock_parcel.updated_at = "2026-09-23T00:00:00Z"
    mock_parcel.geometry = None

    with patch("app.repositories.project.ProjectRepository.get_by_id", AsyncMock(return_value=parent_project)):
        with patch("app.repositories.parcel.ParcelRepository.get_by_id", AsyncMock(return_value=None)):
            with patch("app.repositories.parcel.ParcelRepository.create_with_geometry", AsyncMock(return_value=mock_parcel)):
                with patch("app.repositories.parcel.ParcelRepository.extract_geojson", return_value=parcel_payload["geojson"]):
                    response = await client.post("/api/v1/parcels", json=parcel_payload)
                    assert response.status_code == status.HTTP_201_CREATED
                    data = response.json()
                    assert data["id"] == "TS-HYD-2026-001245"
                    assert data["survey_number"] == "145/2"
                    assert data["center"] == [17.444, 78.683]
                    assert data["geojson"]["type"] == "Polygon"

    app.dependency_overrides.clear()


async def test_field_officer_assignment_scope_restriction(client: AsyncClient, field_officer: User):
    """Verify Field Officer is rejected when attempting to view a parcel not assigned to them (403 Forbidden)."""
    app.dependency_overrides[get_current_user] = lambda: field_officer
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    other_officer_id = uuid.uuid4()
    unassigned_parcel = LandParcel(
        id="TS-HYD-2026-999999",
        survey_number="999/1",
        project_id="NLA-TS-2026-001",
        landowner_name="Unknown Owner",
        state="Telangana",
        district="Hyderabad",
        village="Ghatkesar",
        area_acres=1.0,
        land_type="Agricultural",
        acquisition_status="Proposed",
        compensation_status="Pending",
        possession_status="Not Started",
        assigned_officer_id=other_officer_id,  # Assigned to someone else!
    )
    unassigned_parcel.created_at = "2026-09-23T00:00:00Z"
    unassigned_parcel.updated_at = "2026-09-23T00:00:00Z"

    with patch("app.repositories.parcel.ParcelRepository.get_by_id", AsyncMock(return_value=unassigned_parcel)):
        response = await client.get("/api/v1/parcels/TS-HYD-2026-999999")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert "not assigned" in data["message"].lower()

    app.dependency_overrides.clear()


async def test_citizen_ownership_scope_restriction(client: AsyncClient, citizen_1: User):
    """Verify Citizen is rejected when attempting to access another citizen's parcel (403 Forbidden)."""
    app.dependency_overrides[get_current_user] = lambda: citizen_1
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    other_citizen_parcel = LandParcel(
        id="TS-HYD-2026-001246",
        survey_number="146/1",
        project_id="NLA-TS-2026-001",
        landowner_name="Sita Devi Sharma",
        state="Telangana",
        district="Hyderabad",
        village="Ghatkesar",
        area_acres=1.8,
        land_type="Commercial",
        acquisition_status="Under Verification",
        compensation_status="Under Review",
        possession_status="Demarcated",
        owner_user_id=CITIZEN_2_ID,  # Belongs to Citizen 2
        masked_aadhaar="XXXX-XXXX-3412",
    )
    other_citizen_parcel.created_at = "2026-09-23T00:00:00Z"
    other_citizen_parcel.updated_at = "2026-09-23T00:00:00Z"

    with patch("app.repositories.parcel.ParcelRepository.get_by_id", AsyncMock(return_value=other_citizen_parcel)):
        response = await client.get("/api/v1/parcels/TS-HYD-2026-001246")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert "citizens can only access their authorized" in data["message"].lower()

    app.dependency_overrides.clear()


async def test_parcel_geojson_feature_export(client: AsyncClient, district_user_hyd: User):
    """Verify GET /api/v1/parcels/{id}/geojson exports a standard RFC 7946 GeoJSON Feature."""
    app.dependency_overrides[get_current_user] = lambda: district_user_hyd
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    mock_parcel = LandParcel(
        id="TS-HYD-2026-001245",
        survey_number="145/2",
        project_id="NLA-TS-2026-001",
        landowner_name="Rajesh Kumar",
        state="Telangana",
        district="Hyderabad",
        village="Ghatkesar",
        area_acres=2.5,
        land_type="Agricultural",
        acquisition_status="Compensation Pending",
        compensation_status="Pending",
        possession_status="Demarcated",
        geometry=None,
    )
    mock_parcel.created_at = "2026-09-23T00:00:00Z"
    mock_parcel.updated_at = "2026-09-23T00:00:00Z"

    mock_geojson = {
        "type": "Polygon",
        "coordinates": [
            [[78.681, 17.442], [78.685, 17.442], [78.685, 17.446], [78.681, 17.446], [78.681, 17.442]]
        ],
    }

    with patch("app.repositories.parcel.ParcelRepository.get_by_id", AsyncMock(return_value=mock_parcel)):
        with patch("app.repositories.parcel.ParcelRepository.extract_geojson", return_value=mock_geojson):
            response = await client.get("/api/v1/parcels/TS-HYD-2026-001245/geojson")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["type"] == "Feature"
            assert data["id"] == "TS-HYD-2026-001245"
            assert data["geometry"]["type"] == "Polygon"
            assert data["properties"]["survey_number"] == "145/2"
            assert data["properties"]["state"] == "Telangana"

    app.dependency_overrides.clear()

