"""Authenticating requests that carry a partner API key (see docs/API_KEYS.md).

Checks run cheapest first: shape/env/checksum (no I/O) → cached or DB record
→ constant-time hash comparison → status → method → route tier → path prefix
→ origin. Every failure raises `ApiKeyRejection` with a generic public message
(no oracle for attackers) and the real reason for internal logs.

The record cache lives in Redis for `RECORD_CACHE_SECONDS`. Admin changes
delete the cached entry immediately (`invalidate_api_key_cache`), so a
revocation takes effect at once; if that delete fails, the entry still
expires within the TTL.
"""

import json
from collections.abc import Callable, Generator, Iterable
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from anyio import to_thread
from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlmodel import Session, col, update

from server.config import CONFIG
from server.logger import logger
from server.models.database.api_key_db_model import ApiKey
from server.repositories.api_key_repository import ApiKeyRepository
from server.services.rate_limiter import RateLimitRule
from server.services.redis_client import get_sync_redis
from server.services.security.api_key_crypto import (
    MIN_SECRET_BYTES,
    ApiKeySecretNotConfigured,
    current_env,
    parse_api_key,
    verify_api_key,
)
from server.services.security.api_key_limits import effective_rate_limits
from server.services.security.api_key_scope import path_allowed
from server.utils.brazil_datetime import BrazilDatetime

API_KEY_HEADER = "x-api-key"
# Request-state key holding the ApiKeyIdentity of an authenticated request.
API_KEY_IDENTITY_STATE_KEY = "api_key_identity"
RECORD_CACHE_SECONDS = 60
CACHE_PREFIX = "apikey:"
# last_used_at is written at most once per window per key, not per request.
LAST_USED_PREFIX = "apikey:used:"
LAST_USED_WRITE_SECONDS = 60
# Cached for unknown public_ids too, so guessing ids can't hammer the DB.
MISSING_RECORD = "missing"
READ_ONLY_METHODS = frozenset({"GET", "HEAD"})

INVALID_KEY_DETAIL = "API key inválida, expirada ou revogada."
FORBIDDEN_DETAIL = "Esta API key não tem permissão para esta requisição."


@dataclass(frozen=True)
class ApiKeyRecord:
    """What authentication needs from a key, cacheable as JSON."""

    id: int
    public_id: str
    client_id: int
    key_hash: str
    hash_version: int
    allowed_path_prefixes: list[str]
    allowed_origins: list[str]
    expires_at: datetime
    revoked: bool
    client_active: bool
    # Effective limits: the key's own rows, or the configured defaults.
    rules: list[RateLimitRule]

    @classmethod
    def from_api_key(cls, key: ApiKey) -> "ApiKeyRecord":
        rules, _ = effective_rate_limits(key)
        return cls(
            id=key.id or 0,
            public_id=key.public_id,
            client_id=key.client_id,
            key_hash=key.key_hash,
            hash_version=key.hash_version,
            allowed_path_prefixes=list(key.allowed_path_prefixes),
            allowed_origins=list(key.allowed_origins),
            expires_at=key.expires_at,
            revoked=key.revoked_at is not None,
            client_active=key.client.is_active,
            rules=rules,
        )

    @property
    def is_browser_key(self) -> bool:
        return bool(self.allowed_origins)

    def to_json(self) -> str:
        data = asdict(self)
        data["expires_at"] = self.expires_at.isoformat()
        return json.dumps(data)

    @classmethod
    def from_json(cls, raw: str | bytes) -> "ApiKeyRecord":
        data = json.loads(raw)
        data["expires_at"] = datetime.fromisoformat(data["expires_at"])
        data["rules"] = [RateLimitRule(**rule) for rule in data["rules"]]
        return cls(**data)


@dataclass(frozen=True)
class ApiKeyIdentity:
    """An authenticated key, left on the request state for the rate limiter
    and the access log."""

    key_id: int
    public_id: str
    client_id: int
    rules: list[RateLimitRule]
    is_browser_key: bool


class ApiKeyRejection(Exception):
    def __init__(self, status_code: int, reason: str, public_id: str | None) -> None:
        super().__init__(reason)
        self.status_code = status_code
        # Internal only: logged, never returned to the client.
        self.reason = reason
        self.public_id = public_id

    @property
    def detail(self) -> str:
        if self.status_code == 401:
            return INVALID_KEY_DETAIL
        if self.status_code == 503:
            return "API keys estão temporariamente indisponíveis."
        return FORBIDDEN_DETAIL


RecordLoader = Callable[[str], ApiKeyRecord | None]


class ApiKeyAuthenticator:
    def __init__(
        self,
        load_record: RecordLoader,
        redis: Redis | None,
        *,
        clock: Callable[[], datetime] = BrazilDatetime.now_utc,
    ) -> None:
        # Sync loader (DB); run in a worker thread to keep the loop free.
        self.load_record = load_record
        self.redis = redis
        self.clock = clock

    async def authenticate(
        self,
        plaintext: str,
        *,
        method: str,
        path: str,
        origin: str | None,
        is_public_route: bool | None,
    ) -> ApiKeyIdentity:
        """`is_public_route`: True/False for a matched route, None when no
        route matches (the app answers 404 afterwards)."""
        public_id = parse_api_key(plaintext)
        if public_id is None:
            raise ApiKeyRejection(401, "malformed key, wrong env or bad checksum", None)

        record = await self.__get_record(public_id)
        if record is None:
            raise ApiKeyRejection(401, "unknown public_id", public_id)
        try:
            matches = verify_api_key(plaintext, record.key_hash, record.hash_version)
        except ApiKeySecretNotConfigured:
            logger.error("API_KEY_SECRET is not configured: rejecting API keys")
            raise ApiKeyRejection(503, "API_KEY_SECRET not configured", public_id)
        if not matches:
            raise ApiKeyRejection(401, "hash mismatch", public_id)
        if record.revoked:
            raise ApiKeyRejection(401, "revoked", public_id)
        if not record.client_active:
            raise ApiKeyRejection(401, "client inactive", public_id)
        if record.expires_at <= self.clock():
            raise ApiKeyRejection(401, "expired", public_id)

        if method not in READ_ONLY_METHODS:
            raise ApiKeyRejection(403, f"method {method} not allowed", public_id)
        if is_public_route is False:
            raise ApiKeyRejection(403, "not a public route", public_id)
        if not path_allowed(path, record.allowed_path_prefixes):
            raise ApiKeyRejection(403, f"path {path} out of scope", public_id)
        self.__check_origin(record, origin)

        return ApiKeyIdentity(
            key_id=record.id,
            public_id=record.public_id,
            client_id=record.client_id,
            rules=record.rules,
            is_browser_key=record.is_browser_key,
        )

    @staticmethod
    def __check_origin(record: ApiKeyRecord, origin: str | None) -> None:
        if record.is_browser_key:
            # Browsers always send Origin on cross-origin requests and don't
            # let pages change it. A script can forge it, which is why
            # browser keys are never treated as secret.
            if origin is None or origin.lower() not in record.allowed_origins:
                raise ApiKeyRejection(
                    403, f"origin {origin} not allowed", record.public_id
                )
        elif origin is not None:
            # Server keys must stay on servers: one used from a page is leaked.
            raise ApiKeyRejection(
                403, "server key sent from a browser", record.public_id
            )

    async def __get_record(self, public_id: str) -> ApiKeyRecord | None:
        cache_key = CACHE_PREFIX + public_id
        if self.redis is not None:
            try:
                cached = await self.redis.get(cache_key)
            except (RedisError, OSError):
                cached = None  # fall back to the database
            if cached is not None:
                if cached in (MISSING_RECORD, MISSING_RECORD.encode()):
                    return None
                return ApiKeyRecord.from_json(cached)

        record = await to_thread.run_sync(self.load_record, public_id)

        if self.redis is not None:
            value = record.to_json() if record is not None else MISSING_RECORD
            try:
                await self.redis.set(cache_key, value, ex=RECORD_CACHE_SECONDS)
            except (RedisError, OSError):
                pass
        return record


def invalidate_api_key_cache(public_ids: Iterable[str]) -> None:
    """Drop cached records so admin changes (revoke, deactivate, new scope or
    limits) apply on the next request. Best effort: on Redis errors the
    entries still expire within RECORD_CACHE_SECONDS."""
    keys = [CACHE_PREFIX + public_id for public_id in public_ids]
    redis = None if CONFIG.testing else get_sync_redis()
    if not keys or redis is None:
        return
    try:
        redis.delete(*keys)
    except (RedisError, OSError) as e:
        logger.error(
            f"Failed to invalidate cached API keys (applies within "
            f"{RECORD_CACHE_SECONDS}s): {e}"
        )


SessionProvider = Callable[[], Session | Generator[Session, None, None]]


def _with_session(provider: SessionProvider, work: Callable[[Session], Any]) -> Any:
    """Run `work` with a session from `provider`: either `get_db` (a
    generator) or a test override returning a Session directly."""
    provided = provider()
    if isinstance(provided, Session):
        return work(provided)
    session = next(provided)
    try:
        return work(session)
    finally:
        provided.close()


def db_record_loader(provider: SessionProvider) -> RecordLoader:
    def load(public_id: str) -> ApiKeyRecord | None:
        def work(session: Session) -> ApiKeyRecord | None:
            key = ApiKeyRepository.get_by_public_id(
                public_id=public_id, session=session
            )
            return ApiKeyRecord.from_api_key(key) if key is not None else None

        return _with_session(provider, work)  # type: ignore[no-any-return]

    return load


def db_last_used_writer(provider: SessionProvider) -> Callable[[int], None]:
    def write(key_id: int) -> None:
        def work(session: Session) -> None:
            # A bulk UPDATE, not a SELECT: SQLModel's Session.exec only
            # takes selects, so run it on the session's own connection.
            session.connection().execute(
                update(ApiKey)
                .where(col(ApiKey.id) == key_id)
                .values(last_used_at=BrazilDatetime.now_utc())
            )
            session.commit()

        _with_session(provider, work)

    return write


def db_partner_origins_loader(provider: SessionProvider) -> Callable[[], set[str]]:
    def load() -> set[str]:
        return _with_session(  # type: ignore[no-any-return]
            provider,
            lambda session: ApiKeyRepository.get_active_browser_origins(
                session=session
            ),
        )

    return load


async def should_write_last_used(redis: Redis | None, key_id: int) -> bool:
    """True at most once per LAST_USED_WRITE_SECONDS per key. Without Redis,
    never: one DB write per request isn't worth it."""
    if redis is None:
        return False
    try:
        return bool(
            await redis.set(
                f"{LAST_USED_PREFIX}{key_id}", 1, nx=True, ex=LAST_USED_WRITE_SECONDS
            )
        )
    except (RedisError, OSError):
        return False


def check_api_key_setup() -> str:
    """Startup check: can this server verify API keys? Logs the outcome
    (error without a usable secret) and returns it for the lifespan to print."""
    if len(CONFIG.api_key_secret.encode()) < MIN_SECRET_BYTES:
        message = (
            f"API keys: API_KEY_SECRET is missing or shorter than "
            f"{MIN_SECRET_BYTES} bytes; requests with X-API-Key will get 503"
        )
        logger.error(message)
        return message
    message = f"API keys: ready, accepting up_{current_env()}_ keys"
    logger.info(message)
    return message
