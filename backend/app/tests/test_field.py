import uuid
from datetime import date, datetime, timezone
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import status
from httpx import AsyncClient
from app.api.deps import get_current_user, get_db
from app.core.security import hash_password
from app.main import app
from app.models.field import FieldAssignment, FieldDocument, FieldPhoto
from app.models.parcel import LandParcel
from app.models.user import Role, User

pytestmark = pytest.mark.asyncio

DISTRICT_OFFICER_ID = uuid.uuid4()
FIELD_OFFICER_ID = uuid.uuid4()
OTHER_OFFICER_ID = uuid.uuid4()


def build_test_user(user_id: uuid.UUID, username: str, role_name: str, state: str = "Telangana", district: str = "Hyderabad") -> User:
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
def field_officer():
    return build_test_user(FIELD_OFFICER_ID, "field_agent_vikram", "FIELD_OFFICER")


@pytest.fixture
def other_field_officer():
    return build_test_user(OTHER_OFFICER_ID, "field_agent_other", "FIELD_OFFICER")


@pytest.fixture
def mock_parcel():
    parcel = LandParcel(
        id="TS-HYD-2026-001245",
        survey_number="145/2",
        project_id="NLA-TS-2026-001",
        landowner_name="Rajesh Kumar",
        state="Telangana",
        district="Hyderabad",
        village="Ghatkesar",
        area_acres=2.5,
        land_type="Agricultural",
        acquisition_status="Under Verification",
        compensation_status="Pending",
        possession_status="Not Started",
        assigned_officer_id=FIELD_OFFICER_ID,  # Assigned to Vikram
    )
    parcel.created_at = "2026-09-23T00:00:00Z"
    parcel.updated_at = "2026-09-23T00:00:00Z"
    return parcel


# Valid sample JPEG image bytes (starts with \xff\xd8\xff\xe0)
SAMPLE_JPEG_BYTES = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9"

# Invalid executable binary bytes (MZ executable header)
MALICIOUS_EXE_BYTES = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00\xb8\x00\x00\x00"


# ---------------------------------------------------------------------------
# Test Cases
# ---------------------------------------------------------------------------

async def test_field_assignment_creation(client: AsyncClient, district_officer: User, field_officer: User, mock_parcel: LandParcel):
    """Test District Officer assigning a parcel to a field officer."""
    app.dependency_overrides[get_current_user] = lambda: district_officer
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    payload = {
        "id": "ASN-2026-091",
        "parcel_id": "TS-HYD-2026-001245",
        "assigned_officer_id": str(FIELD_OFFICER_ID),
        "priority": "High",
        "required_tasks": ["GPS Geo-tagging", "Tree Enumeration"],
        "remarks": "Priority corridor parcel",
    }

    mock_assignment = FieldAssignment(
        id=payload["id"],
        parcel_id=payload["parcel_id"],
        project_id="NLA-TS-2026-001",
        assigned_officer_id=FIELD_OFFICER_ID,
        assigned_by_id=DISTRICT_OFFICER_ID,
        assigned_date=date.today(),
        priority="High",
        status="Pending",
        required_tasks=payload["required_tasks"],
        remarks=payload["remarks"],
    )
    mock_assignment.created_at = datetime.now(timezone.utc)
    mock_assignment.updated_at = datetime.now(timezone.utc)

    with patch("app.repositories.parcel.ParcelRepository.get_by_id", AsyncMock(return_value=mock_parcel)):
        with patch("app.repositories.user.UserRepository.get_by_id", AsyncMock(return_value=field_officer)):
            with patch("app.repositories.field.FieldRepository.create_assignment", AsyncMock(return_value=mock_assignment)):
                with patch("app.repositories.audit.AuditRepository.log_action", AsyncMock()):
                    with patch("app.repositories.audit.AuditRepository.create_notification", AsyncMock()):
                        response = await client.post("/api/v1/field/assignments", json=payload)
                        assert response.status_code == status.HTTP_201_CREATED
                        data = response.json()
                        assert data["id"] == "ASN-2026-091"
                        assert data["parcel_id"] == "TS-HYD-2026-001245"
                        assert data["priority"] == "High"
                        assert mock_parcel.assigned_officer_id == FIELD_OFFICER_ID

    app.dependency_overrides.clear()


async def test_field_photo_upload_with_gps(client: AsyncClient, field_officer: User, mock_parcel: LandParcel):
    """Test Field Officer uploading geotagged photo with valid JPEG magic bytes and RTK GPS accuracy."""
    app.dependency_overrides[get_current_user] = lambda: field_officer
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    files = {
        "file": ("boundary_peg.jpg", BytesIO(SAMPLE_JPEG_BYTES), "image/jpeg"),
    }
    data = {
        "parcel_id": "TS-HYD-2026-001245",
        "caption": "North-East Corner Boundary Pillar",
        "latitude": "17.4475",
        "longitude": "78.6789",
        "accuracy_meters": "0.8",
        "photo_type": "Boundary Marker",
    }

    mock_photo = FieldPhoto(
        id="PH-TEST-001",
        parcel_id="TS-HYD-2026-001245",
        uploader_id=FIELD_OFFICER_ID,
        officer_name="Field Agent Vikram",
        caption=data["caption"],
        photo_type=data["photo_type"],
        storage_key="photos/TS-HYD-2026-001245/test.jpg",
        filename="boundary_peg.jpg",
        file_size_bytes=len(SAMPLE_JPEG_BYTES),
        mime_type="image/jpeg",
        document_hash="dummy_hash_sha256",
        photo_url="/static/uploads/photos/test.jpg",
        latitude=17.4475,
        longitude=78.6789,
        accuracy_meters=0.8,
        status="Pending",
        captured_at=datetime.now(timezone.utc),
    )
    mock_photo.created_at = datetime.now(timezone.utc)

    with patch("app.repositories.parcel.ParcelRepository.get_by_id", AsyncMock(return_value=mock_parcel)):
        with patch("app.core.storage.LocalStorageProvider.upload_file", AsyncMock(return_value=("key", "/url"))):
            with patch("app.repositories.field.FieldRepository.create_photo", AsyncMock(return_value=mock_photo)):
                with patch("app.repositories.audit.AuditRepository.log_action", AsyncMock()):
                    response = await client.post("/api/v1/field/photos", data=data, files=files)
                    assert response.status_code == status.HTTP_201_CREATED
                    res_data = response.json()
                    assert res_data["parcel_id"] == "TS-HYD-2026-001245"
                    assert res_data["latitude"] == 17.4475
                    assert res_data["longitude"] == 78.6789
                    assert res_data["accuracy_meters"] == 0.8
                    assert res_data["mime_type"] == "image/jpeg"

    app.dependency_overrides.clear()


async def test_invalid_file_rejected(client: AsyncClient, field_officer: User, mock_parcel: LandParcel):
    """Test that disguised executable (.exe) disguised as .jpg fails file signature validation (422)."""
    app.dependency_overrides[get_current_user] = lambda: field_officer
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    files = {
        "file": ("malicious.jpg", BytesIO(MALICIOUS_EXE_BYTES), "image/jpeg"),
    }
    data = {
        "parcel_id": "TS-HYD-2026-001245",
        "caption": "Malicious Photo",
        "latitude": "17.4475",
        "longitude": "78.6789",
        "accuracy_meters": "1.0",
    }

    with patch("app.repositories.parcel.ParcelRepository.get_by_id", AsyncMock(return_value=mock_parcel)):
        response = await client.post("/api/v1/field/photos", data=data, files=files)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "unsupported or unauthorized file format" in response.json()["message"].lower()

    app.dependency_overrides.clear()


async def test_unauthorized_upload_rejected(client: AsyncClient, other_field_officer: User, mock_parcel: LandParcel):
    """Test that a Field Officer not assigned to a parcel is rejected (403 Forbidden)."""
    app.dependency_overrides[get_current_user] = lambda: other_field_officer  # Not assigned!
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    files = {
        "file": ("boundary_peg.jpg", BytesIO(SAMPLE_JPEG_BYTES), "image/jpeg"),
    }
    data = {
        "parcel_id": "TS-HYD-2026-001245",
        "caption": "Unassigned Photo",
        "latitude": "17.4475",
        "longitude": "78.6789",
    }

    with patch("app.repositories.parcel.ParcelRepository.get_by_id", AsyncMock(return_value=mock_parcel)):
        response = await client.post("/api/v1/field/photos", data=data, files=files)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "not assigned" in response.json()["message"].lower()

    app.dependency_overrides.clear()


async def test_evidence_verification(client: AsyncClient, district_officer: User):
    """Test supervisor approving evidence."""
    app.dependency_overrides[get_current_user] = lambda: district_officer
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    mock_photo = FieldPhoto(
        id="PH-001",
        parcel_id="TS-HYD-2026-001245",
        uploader_id=FIELD_OFFICER_ID,
        officer_name="Field Officer",
        caption="Pillar",
        storage_key="photos/test.jpg",
        filename="test.jpg",
        file_size_bytes=100,
        mime_type="image/jpeg",
        document_hash="hash",
        photo_url="/url",
        latitude=17.0,
        longitude=78.0,
        status="Pending",
    )

    with patch("app.repositories.field.FieldRepository.get_photo_by_id", AsyncMock(return_value=mock_photo)):
        with patch("app.repositories.audit.AuditRepository.log_action", AsyncMock()):
            response = await client.put(
                "/api/v1/field/evidence/photo/PH-001/verify",
                json={"status": "Verified", "remarks": "Boundary verified on ground"},
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["verification_status"] == "Verified"
            assert mock_photo.status == "Verified"

    app.dependency_overrides.clear()


async def test_evidence_rejection_mandatory_remarks(client: AsyncClient, district_officer: User):
    """Test supervisor rejecting evidence fails if mandatory remarks are omitted (422)."""
    app.dependency_overrides[get_current_user] = lambda: district_officer
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    mock_photo = FieldPhoto(
        id="PH-001",
        parcel_id="TS-HYD-2026-001245",
        uploader_id=FIELD_OFFICER_ID,
        officer_name="Field Officer",
        caption="Pillar",
        storage_key="photos/test.jpg",
        filename="test.jpg",
        file_size_bytes=100,
        mime_type="image/jpeg",
        document_hash="hash",
        photo_url="/url",
        latitude=17.0,
        longitude=78.0,
        status="Pending",
    )

    with patch("app.repositories.field.FieldRepository.get_photo_by_id", AsyncMock(return_value=mock_photo)):
        response = await client.put(
            "/api/v1/field/evidence/photo/PH-001/verify",
            json={"status": "Rejected", "remarks": ""},  # Empty remarks!
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "mandatory remarks are required" in response.json()["message"].lower()

    app.dependency_overrides.clear()

