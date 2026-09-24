import uuid
from datetime import date, datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import ScopeChecker
from app.core.exceptions import (
    EntityAlreadyExistsException,
    EntityNotFoundException,
    ForbiddenException,
    ValidationException,
)
from app.core.logging import get_logger
from app.core.storage import compute_sha256
from app.integrations.esign import BaseESignService, get_esign_service
from app.models.consent import ConsentHistory, LandownerConsent
from app.models.user import User
from app.repositories.audit import AuditRepository
from app.repositories.consent import ConsentRepository
from app.repositories.document import DocumentRepository
from app.repositories.parcel import ParcelRepository
from app.schemas.consent import (
    ConsentCreate,
    ConsentHistoryRead,
    ConsentRead,
    ConsentSubmitRequest,
    ConsentVerificationRequest,
    ESignInitiateResponse,
    ESignVerifyResponse,
)

logger = get_logger(__name__)


class ConsentService:
    """Service handling landowner consent workflow, mock eSign simulation, and administrative verification."""

    def __init__(self, session: AsyncSession, esign_service: Optional[BaseESignService] = None):
        self.session = session
        self.consent_repo = ConsentRepository(session)
        self.parcel_repo = ParcelRepository(session)
        self.doc_repo = DocumentRepository(session)
        self.audit_repo = AuditRepository(session)
        self.esign_service = esign_service or get_esign_service()

    def _verify_consent_access(self, user: User, consent: LandownerConsent) -> None:
        """Enforce scoped authorization: citizens can only access their own consent records."""
        if "ADMIN" in user.role_names or "CENTRAL_OFFICIAL" in user.role_names:
            return

        if "CITIZEN" in user.role_names:
            if consent.landowner_user_id == user.id:
                return
            if consent.parcel and consent.parcel.owner_user_id == user.id:
                return
            raise ForbiddenException(
                "Access denied: Citizens may only access their own consent records."
            )

        # Scoped officers (State, District, Field) must have geographic authority over parcel
        if consent.parcel:
            ScopeChecker.verify_parcel_access(user, consent.parcel)

    def _to_history_read(self, h: ConsentHistory) -> ConsentHistoryRead:
        return ConsentHistoryRead(
            id=h.id,
            consent_id=h.consent_id,
            action=h.action,
            from_status=h.from_status,
            to_status=h.to_status,
            performed_by_id=h.performed_by_id,
            performed_by_name=h.performed_by_name,
            performed_by_role=h.performed_by_role,
            remarks=h.remarks,
            timestamp=h.timestamp,
        )

    def _to_consent_read(self, c: LandownerConsent) -> ConsentRead:
        histories = [self._to_history_read(h) for h in (c.history or [])]
        officer_name = c.verifying_officer.full_name if c.verifying_officer else None
        return ConsentRead(
            id=c.id,
            parcel_id=c.parcel_id,
            project_id=c.project_id,
            landowner_user_id=c.landowner_user_id,
            landowner_name=c.landowner_name,
            landowner_aadhaar_masked=c.landowner_aadhaar_masked,
            landowner_phone=c.landowner_phone,
            consent_type=c.consent_type or "VOLUNTARY_ACQUISITION",
            status=c.status,
            submitted_at=c.submitted_at,
            supporting_document_id=c.supporting_document_id,
            esign_simulation_ref=c.esign_simulation_ref,
            esign_verified=c.esign_verified,
            qr_verification_code=c.qr_verification_code,
            document_hash=c.document_hash,
            verifying_officer_id=c.verifying_officer_id,
            verifying_officer_name=officer_name,
            verified_at=c.verified_at,
            verification_remarks=c.verification_remarks,
            rejection_reason=c.rejection_reason,
            created_at=c.created_at or datetime.now(timezone.utc),
            updated_at=c.updated_at or datetime.now(timezone.utc),
            history=histories,
        )

    async def create_consent(
        self,
        consent_in: ConsentCreate,
        current_user: User,
    ) -> ConsentRead:
        """Create a new draft consent record linked to a cadastral land parcel."""
        parcel = await self.parcel_repo.get_by_id(consent_in.parcel_id)
        if not parcel:
            raise EntityNotFoundException("LandParcel", consent_in.parcel_id)

        # Citizen verification: if user is citizen, verify parcel ownership
        landowner_user_id = parcel.owner_user_id
        if "CITIZEN" in current_user.role_names and "ADMIN" not in current_user.role_names:
            if parcel.owner_user_id and parcel.owner_user_id != current_user.id:
                raise ForbiddenException("Citizens can only initiate consent for their own registered parcels.")
            landowner_user_id = current_user.id
        else:
            # Officer or Admin creating consent record
            ScopeChecker.verify_parcel_access(current_user, parcel)

        # Verify supporting document if provided
        if consent_in.supporting_document_id:
            doc = await self.doc_repo.get_document_by_id(consent_in.supporting_document_id)
            if not doc:
                raise EntityNotFoundException("Document", consent_in.supporting_document_id)

        consent_id = consent_in.id or f"CONSENT-{parcel.id}"
        existing = await self.consent_repo.get_consent_by_id(consent_id)
        if existing:
            # If default ID taken, append unique suffix
            consent_id = f"CONSENT-{parcel.id}-{uuid.uuid4().hex[:4].upper()}"

        consent = LandownerConsent(
            id=consent_id,
            parcel_id=parcel.id,
            project_id=parcel.project_id,
            landowner_user_id=landowner_user_id,
            landowner_name=consent_in.landowner_name,
            landowner_aadhaar_masked=consent_in.landowner_aadhaar_masked,
            landowner_phone=consent_in.landowner_phone,
            consent_type=consent_in.consent_type,
            status="DRAFT",
            supporting_document_id=consent_in.supporting_document_id,
            esign_verified=False,
        )
        created = await self.consent_repo.create_consent(consent)

        user_role = current_user.role_names[0] if current_user.role_names else "CITIZEN"
        history = ConsentHistory(
            consent_id=created.id,
            action="CREATED",
            from_status=None,
            to_status="DRAFT",
            performed_by_id=current_user.id,
            performed_by_name=current_user.full_name,
            performed_by_role=user_role,
            remarks=f"Consent record draft initiated for parcel {parcel.id}",
        )
        await self.consent_repo.add_history(history)

        await self.audit_repo.log_action(
            user_id=current_user.id,
            user_name=current_user.full_name,
            role=user_role,
            action="CONSENT_CREATED",
            module="consent",
            entity_type="LandownerConsent",
            entity_id=created.id,
            details=f"Draft consent initiated for parcel '{parcel.id}' by '{current_user.full_name}'",
        )

        refreshed = await self.consent_repo.get_consent_by_id(created.id)
        return self._to_consent_read(refreshed or created)

    async def initiate_mock_esign(
        self,
        consent_id: str,
        current_user: User,
    ) -> ESignInitiateResponse:
        """Initiate simulated eSign OTP dispatch for testing."""
        consent = await self.consent_repo.get_consent_by_id(consent_id)
        if not consent:
            raise EntityNotFoundException("LandownerConsent", consent_id)

        self._verify_consent_access(current_user, consent)

        if consent.status not in ["DRAFT", "PENDING_VERIFICATION", "SUBMITTED"]:
            raise ValidationException(
                f"Cannot initiate eSign on consent in status '{consent.status}'"
            )

        resp = await self.esign_service.initiate_esign(
            consent_id=consent.id,
            signer_name=consent.landowner_name,
            aadhaar_masked=consent.landowner_aadhaar_masked,
        )
        return ESignInitiateResponse(**resp)

    async def verify_mock_esign(
        self,
        transaction_id: str,
        otp_code: str,
        current_user: User,
    ) -> ESignVerifyResponse:
        """Verify simulated OTP and attach mock eSign metadata to consent record."""
        resp = await self.esign_service.verify_otp_and_sign(
            transaction_id=transaction_id,
            otp_code=otp_code,
        )

        consent_id = resp["consent_id"]
        consent = await self.consent_repo.get_consent_by_id(consent_id)
        if not consent:
            raise EntityNotFoundException("LandownerConsent", consent_id)

        self._verify_consent_access(current_user, consent)

        # Update consent with simulation reference
        sim_ref = resp["signature_reference"]
        qr_code = resp["qr_verification_code"]
        doc_hash = compute_sha256(f"{consent.id}:{sim_ref}".encode())

        consent.esign_simulation_ref = sim_ref
        consent.esign_verified = True
        consent.qr_verification_code = qr_code
        consent.document_hash = doc_hash
        await self.consent_repo.update_consent(consent)

        user_role = current_user.role_names[0] if current_user.role_names else "CITIZEN"
        history = ConsentHistory(
            consent_id=consent.id,
            action="MOCK_ESIGN_RECORDED",
            from_status=consent.status,
            to_status=consent.status,
            performed_by_id=current_user.id,
            performed_by_name=current_user.full_name,
            performed_by_role=user_role,
            remarks=f"Simulated eSign recorded. Ref: {sim_ref} (Mock development test only)",
        )
        await self.consent_repo.add_history(history)

        return ESignVerifyResponse(**resp)

    async def submit_consent(
        self,
        consent_id: str,
        submit_in: ConsentSubmitRequest,
        current_user: User,
    ) -> ConsentRead:
        """Submit draft consent for official administrative verification."""
        consent = await self.consent_repo.get_consent_by_id(consent_id)
        if not consent:
            raise EntityNotFoundException("LandownerConsent", consent_id)

        self._verify_consent_access(current_user, consent)

        if consent.status != "DRAFT":
            raise ValidationException(
                f"Consent cannot be submitted from status '{consent.status}'. Must be 'DRAFT'."
            )

        prev_status = consent.status
        consent.status = "SUBMITTED"
        consent.submitted_at = datetime.now(timezone.utc)
        await self.consent_repo.update_consent(consent)

        user_role = current_user.role_names[0] if current_user.role_names else "CITIZEN"
        history = ConsentHistory(
            consent_id=consent.id,
            action="SUBMITTED",
            from_status=prev_status,
            to_status="SUBMITTED",
            performed_by_id=current_user.id,
            performed_by_name=current_user.full_name,
            performed_by_role=user_role,
            remarks=submit_in.remarks or "Consent submitted for official verification",
        )
        await self.consent_repo.add_history(history)

        await self.audit_repo.log_action(
            user_id=current_user.id,
            user_name=current_user.full_name,
            role=user_role,
            action="CONSENT_SUBMITTED",
            module="consent",
            entity_type="LandownerConsent",
            entity_id=consent.id,
            details=f"Consent '{consent.id}' submitted by '{current_user.full_name}'",
        )

        refreshed = await self.consent_repo.get_consent_by_id(consent_id)
        return self._to_consent_read(refreshed or consent)

    async def verify_or_reject_consent(
        self,
        *,
        consent_id: str,
        verify_in: ConsentVerificationRequest,
        current_user: User,
    ) -> ConsentRead:
        """Supervisory officer verifies or rejects landowner consent."""
        if "CITIZEN" in current_user.role_names and "ADMIN" not in current_user.role_names:
            raise ForbiddenException("Citizens cannot verify or reject consent records.")

        consent = await self.consent_repo.get_consent_by_id(consent_id)
        if not consent:
            raise EntityNotFoundException("LandownerConsent", consent_id)

        if consent.parcel:
            ScopeChecker.verify_parcel_access(current_user, consent.parcel)

        prev_status = consent.status
        user_role = current_user.role_names[0] if current_user.role_names else "OFFICER"

        if verify_in.action == "VERIFY":
            consent.status = "VERIFIED"
            consent.verifying_officer_id = current_user.id
            consent.verified_at = datetime.now(timezone.utc)
            consent.verification_remarks = verify_in.remarks
            consent.rejection_reason = None

            # Automatically sync parcel consent status
            if consent.parcel:
                consent.parcel.consent_received = True
                consent.parcel.consent_date = date.today()
                await self.parcel_repo.update(consent.parcel)

            action = "VERIFIED"
            audit_action = "CONSENT_VERIFIED"
        else:
            consent.status = "REJECTED"
            consent.verifying_officer_id = current_user.id
            consent.verified_at = datetime.now(timezone.utc)
            consent.rejection_reason = verify_in.remarks or "Rejected by verifying officer"

            action = "REJECTED"
            audit_action = "CONSENT_REJECTED"

        await self.consent_repo.update_consent(consent)

        history = ConsentHistory(
            consent_id=consent.id,
            action=action,
            from_status=prev_status,
            to_status=consent.status,
            performed_by_id=current_user.id,
            performed_by_name=current_user.full_name,
            performed_by_role=user_role,
            remarks=verify_in.remarks,
        )
        await self.consent_repo.add_history(history)

        await self.audit_repo.log_action(
            user_id=current_user.id,
            user_name=current_user.full_name,
            role=user_role,
            action=audit_action,
            module="consent",
            entity_type="LandownerConsent",
            entity_id=consent.id,
            details=f"Consent '{consent.id}' transitioned to '{consent.status}'. Remarks: {verify_in.remarks}",
        )

        refreshed = await self.consent_repo.get_consent_by_id(consent_id)
        return self._to_consent_read(refreshed or consent)

    async def get_consent(self, consent_id: str, current_user: User) -> ConsentRead:
        """Retrieve consent record by ID after authorization verification."""
        consent = await self.consent_repo.get_consent_by_id(consent_id)
        if not consent:
            raise EntityNotFoundException("LandownerConsent", consent_id)

        self._verify_consent_access(current_user, consent)
        return self._to_consent_read(consent)

    async def get_consent_by_parcel(
        self,
        parcel_id: str,
        current_user: User,
    ) -> Optional[ConsentRead]:
        """Retrieve consent record by parcel ID with access verification."""
        parcel = await self.parcel_repo.get_by_id(parcel_id)
        if not parcel:
            raise EntityNotFoundException("LandParcel", parcel_id)

        ScopeChecker.verify_parcel_access(current_user, parcel)

        consent = await self.consent_repo.get_by_parcel_id(parcel_id)
        if not consent:
            return None
        self._verify_consent_access(current_user, consent)
        return self._to_consent_read(consent)

    async def list_consents(
        self,
        *,
        project_id: Optional[str] = None,
        parcel_id: Optional[str] = None,
        status: Optional[str] = None,
        consent_type: Optional[str] = None,
        current_user: User,
        skip: int = 0,
        limit: int = 50,
    ) -> List[ConsentRead]:
        """List consents filtered by project, parcel, status, and scoped user privileges."""
        landowner_user_id = None
        allowed_states = None
        allowed_districts = None

        if "CITIZEN" in current_user.role_names:
            landowner_user_id = current_user.id
        elif "ADMIN" not in current_user.role_names and "CENTRAL_OFFICIAL" not in current_user.role_names:
            allowed_states = current_user.states or None
            allowed_districts = current_user.districts or None

        consents = await self.consent_repo.list_consents(
            project_id=project_id,
            parcel_id=parcel_id,
            status=status,
            consent_type=consent_type,
            landowner_user_id=landowner_user_id,
            allowed_states=allowed_states,
            allowed_districts=allowed_districts,
            skip=skip,
            limit=limit,
        )
        return [self._to_consent_read(c) for c in consents]

    async def get_consent_history(
        self,
        consent_id: str,
        current_user: User,
    ) -> List[ConsentHistoryRead]:
        """Retrieve full immutable audit history for a consent record."""
        consent = await self.consent_repo.get_consent_by_id(consent_id)
        if not consent:
            raise EntityNotFoundException("LandownerConsent", consent_id)

        self._verify_consent_access(current_user, consent)
        history = await self.consent_repo.get_history(consent_id)
        return [self._to_history_read(h) for h in history]

