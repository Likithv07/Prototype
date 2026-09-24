import hashlib
import os
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Tuple
from app.core.config import settings
from app.core.exceptions import ValidationException
from app.core.logging import get_logger

logger = get_logger(__name__)

# Constants
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "storage" / "uploads"

# Magic byte signatures
MAGIC_BYTES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"RIFF": "image/webp",  # WebP also has WEBP at byte offset 8
    b"%PDF-": "application/pdf",
}


def compute_sha256(file_bytes: bytes) -> str:
    """Compute cryptographic SHA-256 hex digest of file bytes."""
    return hashlib.sha256(file_bytes).hexdigest()


def validate_file_magic_bytes(file_bytes: bytes, filename: str) -> str:
    """Validate actual file signature against allowable types (JPEG, PNG, WebP, PDF).
    
    Prevents executable or malicious files disguised with valid file extensions.
    """
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise ValidationException(
            f"File size exceeds maximum allowable limit of {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."
        )

    if len(file_bytes) < 4:
        raise ValidationException("File is empty or corrupted.")

    detected_mime: Optional[str] = None
    for signature, mime in MAGIC_BYTES.items():
        if file_bytes.startswith(signature):
            if signature == b"RIFF" and b"WEBP" not in file_bytes[:16]:
                continue
            detected_mime = mime
            break

    if not detected_mime:
        raise ValidationException(
            f"Unsupported or unauthorized file format for '{filename}'. Allowed formats: JPEG, PNG, WebP, PDF."
        )

    return detected_mime


class BaseStorageProvider(ABC):
    """Abstract object storage provider interface."""

    @abstractmethod
    async def upload_file(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        directory: str = "evidence",
    ) -> Tuple[str, str]:
        """Save file bytes and return (storage_key, public_url)."""
        pass

    @abstractmethod
    async def get_file(self, storage_key: str) -> Tuple[bytes, str]:
        """Fetch file bytes and content type by storage key."""
        pass

    @abstractmethod
    async def delete_file(self, storage_key: str) -> bool:
        """Remove file by storage key."""
        pass


class LocalStorageProvider(BaseStorageProvider):
    """Local filesystem storage implementation for development and testing."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or UPLOAD_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def upload_file(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        directory: str = "evidence",
    ) -> Tuple[str, str]:
        """Save file to local uploads directory with UUID prefix."""
        target_dir = self.base_dir / directory
        target_dir.mkdir(parents=True, exist_ok=True)

        clean_filename = os.path.basename(filename).replace(" ", "_")
        unique_name = f"{uuid.uuid4().hex[:12]}_{clean_filename}"
        file_path = target_dir / unique_name

        with open(file_path, "wb") as f:
            f.write(file_bytes)

        storage_key = f"{directory}/{unique_name}"
        public_url = f"/static/uploads/{storage_key}"
        logger.info(f"File uploaded successfully to '{storage_key}' ({len(file_bytes)} bytes).")
        return storage_key, public_url

    async def get_file(self, storage_key: str) -> Tuple[bytes, str]:
        """Read file from local uploads directory."""
        file_path = self.base_dir / storage_key
        if not file_path.exists():
            raise ValidationException(f"Stored file '{storage_key}' not found.")

        with open(file_path, "rb") as f:
            content = f.read()

        mime = validate_file_magic_bytes(content, file_path.name)
        return content, mime

    async def delete_file(self, storage_key: str) -> bool:
        """Delete local file."""
        file_path = self.base_dir / storage_key
        if file_path.exists():
            file_path.unlink()
            return True
        return False


def get_storage_provider() -> BaseStorageProvider:
    """Return configured storage provider singleton."""
    return LocalStorageProvider()
