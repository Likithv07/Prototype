import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict
from app.core.exceptions import ValidationException
from app.core.logging import get_logger

logger = get_logger(__name__)


class BaseESignService(ABC):
    """Abstract interface for electronic signature service providers (ESP)."""

    @abstractmethod
    async def initiate_esign(
        self,
        *,
        consent_id: str,
        signer_name: str,
        aadhaar_masked: str,
    ) -> Dict[str, Any]:
        """Initiate eSign request and return transaction reference."""
        pass

    @abstractmethod
    async def verify_otp_and_sign(
        self,
        *,
        transaction_id: str,
        otp_code: str,
    ) -> Dict[str, Any]:
        """Verify OTP and return signed artifact simulation."""
        pass


class MockAadhaarESignService(BaseESignService):
    """Mock implementation of Aadhaar eSign gateway for development and testing.
    
    IMPORTANT: This is explicitly marked as a mock simulation. It does NOT connect
    to UIDAI, C-DAC, NSDL, or any licensed Certifying Authority (CA), and does NOT
    produce legally binding cryptographic signatures under the Indian IT Act 2000.
    """

    is_mock: bool = True
    provider_name: str = "Mock ESP (Development Simulation - NOT connected to UIDAI/C-DAC)"
    disclaimer: str = (
        "This is a local development simulation for testing purposes only and is NOT a "
        "legally binding Aadhaar eSign under Section 3A of the Information Technology Act 2000."
    )

    # In-memory storage for active mock transactions
    _active_transactions: Dict[str, Dict[str, Any]] = {}

    async def initiate_esign(
        self,
        *,
        consent_id: str,
        signer_name: str,
        aadhaar_masked: str,
    ) -> Dict[str, Any]:
        """Generate a simulated transaction ID and simulated OTP."""
        tx_id = f"MOCK-ESIGN-TX-{uuid.uuid4().hex[:12].upper()}"

        # In dev/mock mode, fixed OTP 781923 is accepted (matching frontend demo)
        self._active_transactions[tx_id] = {
            "consent_id": consent_id,
            "signer_name": signer_name,
            "aadhaar_masked": aadhaar_masked,
            "expected_otp": "781923",
            "status": "OTP_SENT",
        }

        logger.info(
            f"[MOCK ESIGN] Initiated simulation for consent '{consent_id}', signer '{signer_name}', tx '{tx_id}'. "
            f"Test OTP: 781923"
        )

        return {
            "is_mock": True,
            "provider_name": self.provider_name,
            "disclaimer": self.disclaimer,
            "transaction_id": tx_id,
            "consent_id": consent_id,
            "status": "OTP_SENT",
            "message": "Simulated OTP dispatched. For testing, use OTP: 781923",
        }

    async def verify_otp_and_sign(
        self,
        *,
        transaction_id: str,
        otp_code: str,
    ) -> Dict[str, Any]:
        """Validate simulated OTP and return mock signature metadata."""
        tx = self._active_transactions.get(transaction_id)
        if not tx:
            raise ValidationException("Invalid or expired eSign transaction ID.")

        clean_otp = otp_code.strip()
        # Accept '781923' or any 6-digit OTP in mock mode
        if clean_otp != "781923" and len(clean_otp) != 6:
            raise ValidationException("Invalid OTP code. For development testing, use '781923'.")

        simulated_signature_ref = f"SIMULATED-ESIGN-{uuid.uuid4().hex[:16].upper()}"
        qr_code = f"BHOOMI-SETU-VERIFY-{tx['consent_id']}-MOCK-ESIGN"

        tx["status"] = "COMPLETED"
        tx["signature_ref"] = simulated_signature_ref

        logger.info(
            f"[MOCK ESIGN] Successfully verified OTP for tx '{transaction_id}'. "
            f"Signature Ref: {simulated_signature_ref}"
        )

        return {
            "is_mock": True,
            "provider_name": self.provider_name,
            "disclaimer": self.disclaimer,
            "transaction_id": transaction_id,
            "consent_id": tx["consent_id"],
            "status": "SIGNED",
            "signer_name": tx["signer_name"],
            "signature_reference": simulated_signature_ref,
            "qr_verification_code": qr_code,
            "message": "Simulated eSign recorded successfully.",
        }


def get_esign_service() -> BaseESignService:
    """Factory returning configured eSign service provider."""
    return MockAadhaarESignService()

