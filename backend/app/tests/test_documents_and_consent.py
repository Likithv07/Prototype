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
from app.models.consent import ConsentHistory, LandownerConsent
from app.models.document import Document, DocumentVersion
from app.models.parcel import LandParcel
from app.models.project import Project
from app.models.user import Role, User

pytestmark = pytest.mark.asyncio

DISTRICT_OFFICER_ID = uuid.uuid4()
FIELD_OFFICER_ID = uuid.uuid4()
CITIZEN_ID = uuid.uuid4()
OTHER_CITIZEN_ID = uuid.uuid4()

SAMPLE_PDF_BYTES = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n"
SAMPLE_PDF_V2_BYTES = b"%PDF-1.4\n% Revision 2 content\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n"
MALICIOUS_EXE_BYTES = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00\xb8\x00\x00\x00"


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
def field_officer():
    return build_test_user(FIELD_OFFICER_ID, "field_agent_vikram", "FIELD_OFFICER")


@pytest.fixture
def citizen_user():
    return build_test_user(CITIZEN_ID, "citizen_rajesh", "CITIZEN")


@pytest.fixture
def other_citizen():
    return build_test_user(OTHER_CITIZEN_ID, "citizen_other", "CITIZEN")


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
        status="SIA_IN_PROGRESS",
    )
    proj.created_at = datetime.now(timezone.utc)
    proj.updated_at = datetime.now(timezone.utc)
    return proj


# ===========================================================================
# 1. Document Management & Strict Versioning Tests
# ===========================================================================

async def test_document_upload_and_v1_creation(
    client: AsyncClient,
    district_officer: User,
    mock_parcel: LandParcel,
    mock_project: Project,
):
    """Test initial document upload creates Document master and Version 1.0 with SHA-256."""
    app.dependency_overrides[get_current_user] = lambda: district_officer
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    doc_id = "DOC-2026-TEST01"
    now = datetime.now(timezone.utc)

    mock_doc = Document(
        id=doc_id,
        title="Preliminary SIA Notification Gazette",
        category="Gazette",
        project_id=mock_project.id,
        parcel_id=mock_parcel.id,
        uploader_id=district_officer.id,
        uploaded_by=district_officer.full_name,
        current_version=1,
        is_verified=False,
    )
    mock_doc.created_at = now
    mock_doc.updated_at = now

    mock_v1 = DocumentVersion(
        id=uuid.uuid4(),
        document_id=doc_id,
        version_number=1,
        version_label="v1.0",
        storage_key=f"statutory/{doc_id}/gazette.pdf",
        filename="gazette.pdf",
        file_size_bytes=len(SAMPLE_PDF_BYTES),
        mime_type="application/pdf",
        checksum_sha256="abc123sha256fake",
        file_url=f"/static/uploads/statutory/{doc_id}/gazette.pdf",
        changelog="Initial statutory filing",
        uploaded_by_id=district_officer.id,
    )
    mock_v1.created_at = now
    mock_doc.versions = [mock_v1]

    with patch("app.repositories.parcel.ParcelRepository.get_by_id", AsyncMock(return_value=mock_parcel)):
        with patch("app.repositories.project.ProjectRepository.get_by_id", AsyncMock(return_value=mock_project)):
            with patch("app.repositories.document.DocumentRepository.get_document_by_id", AsyncMock(side_effect=[None, mock_doc])):
                with patch("app.repositories.document.DocumentRepository.create_document", AsyncMock(return_value=mock_doc)):
                    with patch("app.repositories.document.DocumentRepository.create_version", AsyncMock(return_value=mock_v1)):
                        with patch("app.repositories.audit.AuditRepository.log_action", AsyncMock()):
                            files = {"file": ("gazette.pdf", BytesIO(SAMPLE_PDF_BYTES), "application/pdf")}
                            data = {
                                "title": "Preliminary SIA Notification Gazette",
                                "category": "Gazette",
                                "project_id": mock_project.id,
                                "parcel_id": mock_parcel.id,
                                "custom_id": doc_id,
                            }
                            resp = await client.post("/api/v1/documents", data=data, files=files)
                            assert resp.status_code == status.HTTP_201_CREATED, resp.text
                            body = resp.json()
                            assert body["id"] == doc_id
                            assert body["current_version"] == 1
                            assert body["category"] == "Gazette"
                            assert body["is_verified"] is False
                            assert len(body["versions"]) == 1
                            assert body["versions"][0]["version_label"] == "v1.0"


async def test_document_versioning_no_overwrite(
    client: AsyncClient,
    district_officer: User,
    mock_parcel: LandParcel,
    mock_project: Project,
):
    """Test adding a revised version bumps version number and never overwrites existing version."""
    app.dependency_overrides[get_current_user] = lambda: district_officer
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    doc_id = "DOC-2026-TEST01"
    now = datetime.now(timezone.utc)

    mock_doc = Document(
        id=doc_id,
        title="Preliminary SIA Notification Gazette",
        category="Gazette",
        project_id=mock_project.id,
        parcel_id=mock_parcel.id,
        uploader_id=district_officer.id,
        uploaded_by=district_officer.full_name,
        current_version=1,
        is_verified=True,  # previously verified
    )
    mock_doc.created_at = now
    mock_doc.updated_at = now

    mock_v1 = DocumentVersion(
        id=uuid.uuid4(),
        document_id=doc_id,
        version_number=1,
        version_label="v1.0",
        storage_key=f"statutory/{doc_id}/gazette_v1.pdf",
        filename="gazette_v1.pdf",
        file_size_bytes=len(SAMPLE_PDF_BYTES),
        mime_type="application/pdf",
        checksum_sha256="sha256_v1",
        file_url=f"/static/uploads/statutory/{doc_id}/gazette_v1.pdf",
        changelog="Initial statutory filing",
        uploaded_by_id=district_officer.id,
    )
    mock_v1.created_at = now
    mock_doc.versions = [mock_v1]

    # After version update mock
    mock_v2 = DocumentVersion(
        id=uuid.uuid4(),
        document_id=doc_id,
        version_number=2,
        version_label="v2.0",
        storage_key=f"statutory/{doc_id}/gazette_v2.pdf",
        filename="gazette_v2.pdf",
        file_size_bytes=len(SAMPLE_PDF_V2_BYTES),
        mime_type="application/pdf",
        checksum_sha256="sha256_v2",
        file_url=f"/static/uploads/statutory/{doc_id}/gazette_v2.pdf",
        changelog="Corrigendum for survey numbers",
        uploaded_by_id=district_officer.id,
    )
    mock_v2.created_at = now

    # Updated doc state: version 2, reset verification
    updated_doc = Document(
        id=doc_id,
        title=mock_doc.title,
        category=mock_doc.category,
        project_id=mock_doc.project_id,
        parcel_id=mock_doc.parcel_id,
        uploader_id=district_officer.id,
        uploaded_by=district_officer.full_name,
        current_version=2,
        is_verified=False,  # reset
    )
    updated_doc.created_at = now
    updated_doc.updated_at = now
    updated_doc.versions = [mock_v2, mock_v1]

    with patch("app.repositories.document.DocumentRepository.get_document_by_id", AsyncMock(side_effect=[mock_doc, updated_doc])):
        with patch("app.repositories.document.DocumentRepository.create_version", AsyncMock(return_value=mock_v2)):
            with patch("app.repositories.document.DocumentRepository.update_document", AsyncMock(return_value=updated_doc)):
                with patch("app.repositories.audit.AuditRepository.log_action", AsyncMock()):
                    files = {"file": ("gazette_v2.pdf", BytesIO(SAMPLE_PDF_V2_BYTES), "application/pdf")}
                    data = {"changelog": "Corrigendum for survey numbers"}
                    resp = await client.post(f"/api/v1/documents/{doc_id}/versions", data=data, files=files)
                    assert resp.status_code == status.HTTP_201_CREATED, resp.text
                    body = resp.json()
                    assert body["current_version"] == 2
                    assert body["is_verified"] is False
                    assert len(body["versions"]) == 2
                    assert body["versions"][0]["version_label"] == "v2.0"
                    assert body["versions"][1]["version_label"] == "v1.0"


async def test_document_invalid_magic_bytes_rejected(client: AsyncClient, district_officer: User):
    """Test spoofed or malicious binary executable is rejected by magic byte validator."""
    app.dependency_overrides[get_current_user] = lambda: district_officer
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    files = {"file": ("corrupted.pdf", BytesIO(MALICIOUS_EXE_BYTES), "application/pdf")}
    data = {
        "title": "Corrupt Document",
        "category": "Gazette",
    }
    resp = await client.post("/api/v1/documents", data=data, files=files)
    assert resp.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]


async def test_document_download_authorization(
    client: AsyncClient,
    citizen_user: User,
    other_citizen: User,
    mock_parcel: LandParcel,
):
    """Test citizens are forbidden from downloading documents of parcels they do not own."""
    # other_citizen tries to access document belonging to citizen_user's parcel
    app.dependency_overrides[get_current_user] = lambda: other_citizen
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    doc_id = "DOC-PRIVATE-001"
    mock_doc = Document(
        id=doc_id,
        title="Land Title Deed",
        category="Title Deed",
        parcel_id=mock_parcel.id,
        uploader_id=citizen_user.id,
        uploaded_by=citizen_user.full_name,
        current_version=1,
    )
    mock_doc.parcel = mock_parcel  # owned by CITIZEN_ID, not OTHER_CITIZEN_ID

    with patch("app.repositories.document.DocumentRepository.get_document_by_id", AsyncMock(return_value=mock_doc)):
        resp = await client.get(f"/api/v1/documents/{doc_id}/download")
        assert resp.status_code == status.HTTP_403_FORBIDDEN


async def test_document_verification_flow(
    client: AsyncClient,
    district_officer: User,
    citizen_user: User,
    mock_parcel: LandParcel,
):
    """Test authorized officer can verify a document, while a citizen cannot."""
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    doc_id = "DOC-VERIFY-001"
    now = datetime.now(timezone.utc)
    mock_doc = Document(
        id=doc_id,
        title="Verified Title Deed",
        category="Title Deed",
        parcel_id=mock_parcel.id,
        uploader_id=citizen_user.id,
        uploaded_by=citizen_user.full_name,
        current_version=1,
        is_verified=False,
    )
    mock_doc.created_at = now
    mock_doc.updated_at = now
    mock_doc.parcel = mock_parcel

    verified_doc = Document(
        id=doc_id,
        title=mock_doc.title,
        category=mock_doc.category,
        parcel_id=mock_parcel.id,
        uploader_id=citizen_user.id,
        uploaded_by=citizen_user.full_name,
        current_version=1,
        is_verified=True,
        verified_by_id=district_officer.id,
        verified_at=now,
        verification_remarks="Document verified with Tehsil records.",
    )
    verified_doc.created_at = now
    verified_doc.updated_at = now
    verified_doc.parcel = mock_parcel

    # 1. District Officer verifies
    app.dependency_overrides[get_current_user] = lambda: district_officer
    with patch("app.repositories.document.DocumentRepository.get_document_by_id", AsyncMock(side_effect=[mock_doc, verified_doc])):
        with patch("app.repositories.document.DocumentRepository.update_document", AsyncMock(return_value=verified_doc)):
            with patch("app.repositories.audit.AuditRepository.log_action", AsyncMock()):
                resp = await client.put(
                    f"/api/v1/documents/{doc_id}/verify",
                    json={"is_verified": True, "verification_remarks": "Document verified with Tehsil records."},
                )
                assert resp.status_code == status.HTTP_200_OK, resp.text
                assert resp.json()["is_verified"] is True
                assert resp.json()["verification_remarks"] == "Document verified with Tehsil records."

    # 2. Citizen attempt is forbidden
    app.dependency_overrides[get_current_user] = lambda: citizen_user
    resp2 = await client.put(
        f"/api/v1/documents/{doc_id}/verify",
        json={"is_verified": True, "verification_remarks": "Citizen self verify attempt"},
    )
    assert resp2.status_code == status.HTTP_403_FORBIDDEN


# ===========================================================================
# 2. Landowner Consent & Mock E-Sign Simulation Tests
# ===========================================================================

async def test_consent_creation_draft(
    client: AsyncClient,
    citizen_user: User,
    mock_parcel: LandParcel,
):
    """Test citizen initiating draft consent for their own parcel."""
    app.dependency_overrides[get_current_user] = lambda: citizen_user
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    consent_id = f"CONSENT-{mock_parcel.id}"
    now = datetime.now(timezone.utc)

    mock_consent = LandownerConsent(
        id=consent_id,
        parcel_id=mock_parcel.id,
        project_id=mock_parcel.project_id,
        landowner_user_id=citizen_user.id,
        landowner_name="Rajesh Kumar",
        landowner_aadhaar_masked="XXXX-XXXX-1245",
        landowner_phone="+91 98765 43210",
        consent_type="VOLUNTARY_ACQUISITION",
        status="DRAFT",
        esign_verified=False,
    )
    mock_consent.created_at = now
    mock_consent.updated_at = now
    mock_consent.parcel = mock_parcel

    with patch("app.repositories.parcel.ParcelRepository.get_by_id", AsyncMock(return_value=mock_parcel)):
        with patch("app.repositories.consent.ConsentRepository.get_consent_by_id", AsyncMock(side_effect=[None, mock_consent])):
            with patch("app.repositories.consent.ConsentRepository.create_consent", AsyncMock(return_value=mock_consent)):
                with patch("app.repositories.consent.ConsentRepository.add_history", AsyncMock()):
                    with patch("app.repositories.audit.AuditRepository.log_action", AsyncMock()):
                        payload = {
                            "parcel_id": mock_parcel.id,
                            "landowner_name": "Rajesh Kumar",
                            "landowner_aadhaar_masked": "XXXX-XXXX-1245",
                            "landowner_phone": "+91 98765 43210",
                            "consent_type": "VOLUNTARY_ACQUISITION",
                        }
                        resp = await client.post("/api/v1/consent", json=payload)
                        assert resp.status_code == status.HTTP_201_CREATED, resp.text
                        data = resp.json()
                        assert data["id"] == consent_id
                        assert data["status"] == "DRAFT"
                        assert data["esign_verified"] is False


async def test_mock_esign_simulation_flow(
    client: AsyncClient,
    citizen_user: User,
    mock_parcel: LandParcel,
):
    """Test simulated Aadhaar OTP generation and verification without claiming to be live UIDAI service."""
    app.dependency_overrides[get_current_user] = lambda: citizen_user
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    consent_id = f"CONSENT-{mock_parcel.id}"
    now = datetime.now(timezone.utc)

    mock_consent = LandownerConsent(
        id=consent_id,
        parcel_id=mock_parcel.id,
        project_id=mock_parcel.project_id,
        landowner_user_id=citizen_user.id,
        landowner_name="Rajesh Kumar",
        landowner_aadhaar_masked="XXXX-XXXX-1245",
        status="DRAFT",
        esign_verified=False,
    )
    mock_consent.created_at = now
    mock_consent.updated_at = now
    mock_consent.parcel = mock_parcel

    # 1. Initiate simulated OTP
    with patch("app.repositories.consent.ConsentRepository.get_consent_by_id", AsyncMock(return_value=mock_consent)):
        initiate_resp = await client.post(f"/api/v1/consent/{consent_id}/esign/initiate")
        assert initiate_resp.status_code == status.HTTP_200_OK, initiate_resp.text
        init_data = initiate_resp.json()
        assert init_data["is_mock"] is True
        assert "NOT a legally binding Aadhaar eSign" in init_data["disclaimer"]
        assert "781923" in init_data["message"]
        tx_id = init_data["transaction_id"]

    # 2. Verify OTP with simulated code 781923
    with patch("app.repositories.consent.ConsentRepository.get_consent_by_id", AsyncMock(return_value=mock_consent)):
        with patch("app.repositories.consent.ConsentRepository.update_consent", AsyncMock(return_value=mock_consent)):
            with patch("app.repositories.consent.ConsentRepository.add_history", AsyncMock()):
                verify_resp = await client.post(
                    f"/api/v1/consent/{consent_id}/esign/verify",
                    json={"transaction_id": tx_id, "otp_code": "781923"},
                )
                assert verify_resp.status_code == status.HTTP_200_OK, verify_resp.text
                ver_data = verify_resp.json()
                assert ver_data["is_mock"] is True
                assert ver_data["status"] == "SIGNED"
                assert ver_data["signature_reference"].startswith("SIMULATED-ESIGN-")
                assert "BHOOMI-SETU-VERIFY" in ver_data["qr_verification_code"]


async def test_consent_submit_and_officer_verification(
    client: AsyncClient,
    citizen_user: User,
    district_officer: User,
    mock_parcel: LandParcel,
):
    """Test citizen submitting consent and District Officer officially verifying it."""
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    consent_id = f"CONSENT-{mock_parcel.id}"
    now = datetime.now(timezone.utc)

    # Consent in DRAFT state with eSign completed
    draft_consent = LandownerConsent(
        id=consent_id,
        parcel_id=mock_parcel.id,
        project_id=mock_parcel.project_id,
        landowner_user_id=citizen_user.id,
        landowner_name="Rajesh Kumar",
        landowner_aadhaar_masked="XXXX-XXXX-1245",
        status="DRAFT",
        esign_verified=True,
        esign_simulation_ref="SIMULATED-ESIGN-998877",
    )
    draft_consent.created_at = now
    draft_consent.updated_at = now
    draft_consent.parcel = mock_parcel

    submitted_consent = LandownerConsent(
        id=consent_id,
        parcel_id=mock_parcel.id,
        project_id=mock_parcel.project_id,
        landowner_user_id=citizen_user.id,
        landowner_name="Rajesh Kumar",
        landowner_aadhaar_masked="XXXX-XXXX-1245",
        status="SUBMITTED",
        submitted_at=now,
        esign_verified=True,
        esign_simulation_ref="SIMULATED-ESIGN-998877",
    )
    submitted_consent.created_at = now
    submitted_consent.updated_at = now
    submitted_consent.parcel = mock_parcel

    verified_consent = LandownerConsent(
        id=consent_id,
        parcel_id=mock_parcel.id,
        project_id=mock_parcel.project_id,
        landowner_user_id=citizen_user.id,
        landowner_name="Rajesh Kumar",
        landowner_aadhaar_masked="XXXX-XXXX-1245",
        status="VERIFIED",
        submitted_at=now,
        esign_verified=True,
        esign_simulation_ref="SIMULATED-ESIGN-998877",
        verifying_officer_id=district_officer.id,
        verified_at=now,
        verification_remarks="Consent and Form 15 validated with revenue records.",
    )
    verified_consent.created_at = now
    verified_consent.updated_at = now
    verified_consent.parcel = mock_parcel

    # 1. Citizen submits
    app.dependency_overrides[get_current_user] = lambda: citizen_user
    with patch("app.repositories.consent.ConsentRepository.get_consent_by_id", AsyncMock(side_effect=[draft_consent, submitted_consent])):
        with patch("app.repositories.consent.ConsentRepository.update_consent", AsyncMock(return_value=submitted_consent)):
            with patch("app.repositories.consent.ConsentRepository.add_history", AsyncMock()):
                with patch("app.repositories.audit.AuditRepository.log_action", AsyncMock()):
                    sub_resp = await client.post(
                        f"/api/v1/consent/{consent_id}/submit",
                        json={"remarks": "Submitting voluntary acquisition consent under Section 2(2)"},
                    )
                    assert sub_resp.status_code == status.HTTP_200_OK, sub_resp.text
                    assert sub_resp.json()["status"] == "SUBMITTED"

    # 2. District Officer verifies
    app.dependency_overrides[get_current_user] = lambda: district_officer
    with patch("app.repositories.consent.ConsentRepository.get_consent_by_id", AsyncMock(side_effect=[submitted_consent, verified_consent])):
        with patch("app.repositories.consent.ConsentRepository.update_consent", AsyncMock(return_value=verified_consent)):
            with patch("app.repositories.parcel.ParcelRepository.update", AsyncMock(return_value=mock_parcel)):
                with patch("app.repositories.consent.ConsentRepository.add_history", AsyncMock()):
                    with patch("app.repositories.audit.AuditRepository.log_action", AsyncMock()):
                        ver_resp = await client.put(
                            f"/api/v1/consent/{consent_id}/verify",
                            json={"action": "VERIFY", "remarks": "Consent and Form 15 validated with revenue records."},
                        )
                        assert ver_resp.status_code == status.HTTP_200_OK, ver_resp.text
                        assert ver_resp.json()["status"] == "VERIFIED"
                        assert ver_resp.json()["verification_remarks"] == "Consent and Form 15 validated with revenue records."

