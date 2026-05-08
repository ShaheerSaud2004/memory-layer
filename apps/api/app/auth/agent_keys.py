import hashlib
import secrets
from uuid import UUID

from passlib.context import CryptContext

_agent_pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def generate_agent_api_key() -> tuple[str, str, str]:
    secret = secrets.token_urlsafe(32)
    full = f"aml_{secret}"
    prefix = full[:12]
    key_hash = _agent_pwd.hash(full)
    return full, prefix, key_hash


def verify_agent_api_key(raw_key: str, key_hash: str) -> bool:
    return _agent_pwd.verify(raw_key, key_hash)


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()
