from __future__ import annotations

import secrets
import string


class PlayerCodeGenerator:
    """Utility class for generating human-friendly unique codes."""

    ALPHABET = string.ascii_uppercase + string.digits

    @classmethod
    def generate(cls, length: int = 8) -> str:
        return ''.join(secrets.choice(cls.ALPHABET) for _ in range(length))
