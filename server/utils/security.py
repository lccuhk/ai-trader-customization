"""
Security Utilities

Password hashing, token generation, and other security-related functions.
Uses PBKDF2-SHA256 with a random salt for password hashing.
"""

import hashlib
import secrets
import base64
from datetime import datetime, timedelta
from typing import Optional

from config import settings

# PBKDF2 parameters
PBKDF2_ITERATIONS = 600_000
SALT_BYTES = 16
HASH_ALGORITHM = 'sha256'


def hash_password(password: str) -> str:
    """
    Hash a password using PBKDF2-SHA256 with a random salt.
    Returns a base64-encoded string in the format: salt$hash
    """
    salt = secrets.token_bytes(SALT_BYTES)
    key = hashlib.pbkdf2_hmac(
        HASH_ALGORITHM,
        password.encode('utf-8'),
        salt,
        PBKDF2_ITERATIONS
    )
    salt_b64 = base64.b64encode(salt).decode('ascii')
    hash_b64 = base64.b64encode(key).decode('ascii')
    return f"{salt_b64}${hash_b64}"


def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verify a password against a stored hash created by hash_password.
    """
    try:
        salt_b64, hash_b64 = stored_hash.split('$', 1)
        salt = base64.b64decode(salt_b64)
        expected_key = base64.b64decode(hash_b64)

        key = hashlib.pbkdf2_hmac(
            HASH_ALGORITHM,
            password.encode('utf-8'),
            salt,
            PBKDF2_ITERATIONS
        )
        return secrets.compare_digest(key, expected_key)
    except (ValueError, AttributeError):
        # Legacy SHA-256 fallback (for existing users)
        return hashlib.sha256(password.encode()).hexdigest() == stored_hash


def generate_token() -> str:
    return secrets.token_hex(32)


def get_token_expiry() -> datetime:
    return datetime.now() + timedelta(days=settings.TOKEN_EXPIRE_DAYS)
