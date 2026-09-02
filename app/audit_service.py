import asyncio
import json
import os
import uuid
from datetime import datetime, timezone

from cryptography.fernet import Fernet


class AuditService:
    """
    Mock audit database that stores:
      • original_message: encrypted (Fernet symmetric encryption)
      • sanitized_message: plaintext
    Persists to a local JSON file.
    """
    DB_PATH = "audit_db.json"

    # Demo key — in production load from env var / KMS (e.g., AWS Secrets Manager)
    _key = Fernet.generate_key()
    _fernet = Fernet(_key)

    @classmethod
    async def log_inquiry(
        cls,
        user_id: str,
        original_message: str,
        sanitized_message: str,
        redactions: list[str]
    ) -> str:
        """Async wrapper so file I/O doesn't block the event loop."""
        return await asyncio.to_thread(
            cls._sync_log,
            user_id,
            original_message,
            sanitized_message,
            redactions
        )

    @classmethod
    def _sync_log(cls, user_id, original_message, sanitized_message, redactions) -> str:
        audit_id = str(uuid.uuid4())
        encrypted_original = cls._fernet.encrypt(original_message.encode()).decode()

        entry = {
            "audit_id": audit_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "original_message_encrypted": encrypted_original,
            "sanitized_message_plaintext": sanitized_message,
            "redactions_found": redactions
        }

        db = []
        if os.path.exists(cls.DB_PATH):
            with open(cls.DB_PATH, "r", encoding="utf-8") as f:
                try:
                    db = json.load(f)
                except json.JSONDecodeError:
                    db = []

        db.append(entry)

        with open(cls.DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2)

        return audit_id

    @classmethod
    def decrypt_message(cls, encrypted_b64: str) -> str:
        """Utility to verify / decrypt an audited original message."""
        return cls._fernet.decrypt(encrypted_b64.encode()).decode()