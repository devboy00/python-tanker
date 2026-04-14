import base64
import hashlib
import hmac
import json
import time
from typing import Any

from app.core.config import get_settings


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _sign(signing_input: bytes, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return _b64url_encode(digest)


def create_access_token(subject: str, expires_in_seconds: int | None = None) -> str:
    settings = get_settings()
    if settings.secret_key == "change-me":
        raise ValueError("SECRET_KEY must be configured before issuing tokens.")

    now = int(time.time())
    ttl = expires_in_seconds or settings.access_token_expire_minutes * 60

    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": subject, "iat": now, "exp": now + ttl}

    header_part = _b64url_encode(json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    payload_part = _b64url_encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    signing_input = f"{header_part}.{payload_part}".encode("ascii")
    signature_part = _sign(signing_input, settings.secret_key)

    return f"{header_part}.{payload_part}.{signature_part}"


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    if settings.secret_key == "change-me":
        raise ValueError("SECRET_KEY must be configured before verifying tokens.")

    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Malformed token.")

    header_part, payload_part, signature_part = parts
    signing_input = f"{header_part}.{payload_part}".encode("ascii")
    expected_signature = _sign(signing_input, settings.secret_key)
    if not hmac.compare_digest(signature_part, expected_signature):
        raise ValueError("Invalid token signature.")

    try:
        payload = json.loads(_b64url_decode(payload_part))
    except Exception as exc:
        raise ValueError("Invalid token payload.") from exc

    exp = payload.get("exp")
    sub = payload.get("sub")
    if not isinstance(exp, int) or not isinstance(sub, str) or not sub:
        raise ValueError("Invalid token claims.")
    if exp < int(time.time()):
        raise ValueError("Token expired.")

    return payload
