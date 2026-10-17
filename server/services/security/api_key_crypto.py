"""Partner API key generation, parsing and hashing (see docs/API_KEYS.md).

Format: ``up_<env>_<public_id>_<secret>_<checksum>``, e.g.
``up_live_a1b2c3d4e5f60718_<43 base62 chars>_<6 base62 chars>``.

- ``env``: ``live`` (production), ``test`` (staging) or ``dev`` (development).
  A server only accepts keys of its own environment.
- ``public_id``: 16 hex chars, the non-secret lookup id.
- ``secret``: 43 base62 chars (~256 bits).
- ``checksum``: CRC32 of everything before it, as 6 base62 chars. Not a
  security control: it lets typo'd or truncated keys be rejected before any
  database or HMAC work, and lets secret scanners confirm a match.

Only an HMAC-SHA256 of the full key (keyed with ``API_KEY_SECRET``) is ever
stored. The keys are 256-bit random, so a slow password hash would only burn
CPU; the server-side secret means a leaked database dump can't verify keys.
"""

import hashlib
import hmac
import re
import secrets
import zlib
from dataclasses import dataclass
from enum import StrEnum

from server.config import CONFIG

KEY_PREFIX = "up"
PUBLIC_ID_LENGTH = 16
SECRET_LENGTH = 43
CHECKSUM_LENGTH = 6
BASE62_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
MIN_SECRET_BYTES = 32
CURRENT_HASH_VERSION = 1


class ApiKeyEnv(StrEnum):
    LIVE = "live"
    TEST = "test"
    DEV = "dev"


# Shared with partners for secret scanning (gitleaks, trufflehog, GitHub
# custom patterns) and reusable for log redaction.
API_KEY_PATTERN = re.compile(
    rf"\b{KEY_PREFIX}_(?:{'|'.join(ApiKeyEnv)})_[0-9a-f]{{{PUBLIC_ID_LENGTH}}}"
    rf"_[0-9A-Za-z]{{{SECRET_LENGTH}}}_[0-9A-Za-z]{{{CHECKSUM_LENGTH}}}\b"
)
_FULL_MATCH = re.compile(
    rf"{KEY_PREFIX}_(?P<env>{'|'.join(ApiKeyEnv)})_(?P<public_id>[0-9a-f]{{{PUBLIC_ID_LENGTH}}})"
    rf"_(?P<secret>[0-9A-Za-z]{{{SECRET_LENGTH}}})_(?P<checksum>[0-9A-Za-z]{{{CHECKSUM_LENGTH}}})"
)


class ApiKeySecretNotConfigured(RuntimeError):
    def __init__(self) -> None:
        super().__init__(
            f"API_KEY_SECRET must be set to at least {MIN_SECRET_BYTES} bytes"
        )


@dataclass(frozen=True)
class GeneratedApiKey:
    """A freshly generated key. `plaintext` is shown to the admin once and
    never stored."""

    plaintext: str
    public_id: str
    key_hash: str
    hash_version: int


def current_env() -> ApiKeyEnv:
    """The key environment this server accepts and issues, from ENVIRONMENT."""
    environment = CONFIG.environment.strip().lower()
    if environment == "production":
        return ApiKeyEnv.LIVE
    if environment == "staging":
        return ApiKeyEnv.TEST
    return ApiKeyEnv.DEV


def _base62(number: int, length: int) -> str:
    chars = []
    for _ in range(length):
        number, remainder = divmod(number, 62)
        chars.append(BASE62_ALPHABET[remainder])
    return "".join(reversed(chars))


def _checksum(body: str) -> str:
    # CRC32 < 2**32 < 62**6, so 6 base62 chars always fit it.
    return _base62(zlib.crc32(body.encode()), CHECKSUM_LENGTH)


def _secret_bytes(version: int) -> bytes:
    if version != CURRENT_HASH_VERSION:
        raise ValueError(f"Unknown API key hash version {version}")
    secret = CONFIG.api_key_secret.encode()
    if len(secret) < MIN_SECRET_BYTES:
        raise ApiKeySecretNotConfigured()
    return secret


def hash_api_key(plaintext: str, version: int = CURRENT_HASH_VERSION) -> str:
    """HMAC-SHA256 hex of the full key, keyed with API_KEY_SECRET."""
    return hmac.new(
        _secret_bytes(version), plaintext.encode(), hashlib.sha256
    ).hexdigest()


def generate_api_key(env: ApiKeyEnv | None = None) -> GeneratedApiKey:
    env = env if env is not None else current_env()
    public_id = secrets.token_hex(PUBLIC_ID_LENGTH // 2)
    secret = "".join(secrets.choice(BASE62_ALPHABET) for _ in range(SECRET_LENGTH))
    body = f"{KEY_PREFIX}_{env}_{public_id}_{secret}"
    plaintext = f"{body}_{_checksum(body)}"
    return GeneratedApiKey(
        plaintext=plaintext,
        public_id=public_id,
        key_hash=hash_api_key(plaintext),
        hash_version=CURRENT_HASH_VERSION,
    )


def parse_api_key(plaintext: str, env: ApiKeyEnv | None = None) -> str | None:
    """The key's public_id if its shape, environment and checksum are valid,
    else None. Cheap: no database or HMAC work."""
    match = _FULL_MATCH.fullmatch(plaintext)
    if match is None:
        return None
    if match["env"] != (env if env is not None else current_env()):
        return None
    body = plaintext[: -(CHECKSUM_LENGTH + 1)]
    if not hmac.compare_digest(match["checksum"], _checksum(body)):
        return None
    return match["public_id"]


def verify_api_key(plaintext: str, key_hash: str, hash_version: int) -> bool:
    """Constant-time comparison against the stored hash."""
    return hmac.compare_digest(hash_api_key(plaintext, hash_version), key_hash)
