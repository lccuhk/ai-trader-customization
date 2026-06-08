"""
Security Utilities

Password hashing, token generation, and other security-related functions.
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional

from config import settings


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


def generate_token() -> str:
    return secrets.token_hex(32)


def get_token_expiry() -> datetime:
    return datetime.now() + timedelta(days=settings.TOKEN_EXPIRE_DAYS)
