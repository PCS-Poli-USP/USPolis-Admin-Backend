"""Sealing a partner API key for one-time delivery by link (see
docs/API_KEYS.md, "Entrega por link").

The key is encrypted with AES-256-GCM under a key derived (HKDF-SHA256) from
a random 256-bit ``token`` that only exists in the link's URL fragment
(``/api-key/<link_id>#<token>``). The database keeps the ciphertext, nonce and
salt, never the token: a database dump, even with ``API_KEY_SECRET``, can't
open it.

- No token hash is stored: GCM's authentication tag already rejects a wrong
  token (``InvalidTag``).
- ``link_id`` is the associated data, binding each ciphertext to its own row.
- The token is 256-bit random, not a password, so HKDF is enough; a slow KDF
  would only burn CPU (same reasoning as api_key_crypto's HMAC).
"""

import secrets
from dataclasses import dataclass

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from server.config import CONFIG

TOKEN_BYTES = 32
KEY_BYTES = 32
NONCE_BYTES = 12
SALT_BYTES = 16
HKDF_INFO = b"uspolis-api-key-link-v1"


@dataclass(frozen=True)
class SealedApiKey:
    """`token` goes into the link and is never stored; the rest is."""

    token: str
    ciphertext: bytes
    nonce: bytes
    salt: bytes


def _derive_key(token: str, salt: bytes) -> bytes:
    return HKDF(
        algorithm=hashes.SHA256(), length=KEY_BYTES, salt=salt, info=HKDF_INFO
    ).derive(token.encode())


def generate_link_id() -> str:
    """The link's non-secret id, used in the URL path."""
    return secrets.token_hex(8)


def delivery_link_url(link_id: str, token: str) -> str:
    """The token goes in the fragment, which browsers never send to a
    server: it stays out of access logs and Referer headers. Always built
    here from FRONTEND_URL, never taken from a client."""
    return f"{CONFIG.frontend_url.rstrip('/')}/api-key/{link_id}#{token}"


def seal_api_key(plaintext: str, link_id: str) -> SealedApiKey:
    token = secrets.token_urlsafe(TOKEN_BYTES)
    salt = secrets.token_bytes(SALT_BYTES)
    nonce = secrets.token_bytes(NONCE_BYTES)
    ciphertext = AESGCM(_derive_key(token, salt)).encrypt(
        nonce, plaintext.encode(), link_id.encode()
    )
    return SealedApiKey(token=token, ciphertext=ciphertext, nonce=nonce, salt=salt)


def open_sealed_api_key(
    *, token: str, link_id: str, ciphertext: bytes, nonce: bytes, salt: bytes
) -> str | None:
    """The plaintext key, or None if the token (or any stored part) is wrong."""
    try:
        plaintext = AESGCM(_derive_key(token, salt)).decrypt(
            nonce, ciphertext, link_id.encode()
        )
    except InvalidTag:
        return None
    return plaintext.decode()
