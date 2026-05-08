from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
import hashlib
import os

from app.core.config import get_settings


def _kek() -> bytes:
    s = get_settings().master_key.encode("utf-8")
    return hashlib.sha256(s).digest()


def encrypt_field(plaintext: str, tenant_id: str) -> tuple[str, str]:
    key = hashlib.sha256(_kek() + tenant_id.encode()).digest()
    aes = AESGCM(key)
    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, plaintext.encode("utf-8"), None)
    blob = base64.b64encode(nonce + ct).decode("ascii")
    return blob, base64.b64encode(nonce).decode("ascii")


def decrypt_field(blob: str, tenant_id: str) -> str:
    raw = base64.b64decode(blob)
    nonce, ct = raw[:12], raw[12:]
    key = hashlib.sha256(_kek() + tenant_id.encode()).digest()
    aes = AESGCM(key)
    return aes.decrypt(nonce, ct, None).decode("utf-8")


def generate_dek() -> bytes:
    return os.urandom(32)


def wrap_dek(dek: bytes, tenant_id: str) -> tuple[str, str]:
    key = hashlib.sha256(_kek() + tenant_id.encode()).digest()
    aes = AESGCM(key)
    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, dek, None)
    blob = base64.b64encode(nonce + ct).decode("ascii")
    return blob, base64.b64encode(nonce).decode("ascii")


def unwrap_dek(blob: str, tenant_id: str) -> bytes:
    raw = base64.b64decode(blob)
    nonce, ct = raw[:12], raw[12:]
    key = hashlib.sha256(_kek() + tenant_id.encode()).digest()
    aes = AESGCM(key)
    return aes.decrypt(nonce, ct, None)
