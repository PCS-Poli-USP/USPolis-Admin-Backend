from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload
from sqlmodel import Session, col, func, select

from server.models.database.api_client_db_model import ApiClient
from server.models.database.api_key_db_model import ApiKey
from server.models.database.api_key_rate_limit_db_model import ApiKeyRateLimit
from server.models.database.user_db_model import User
from server.models.http.requests.api_key_request_models import (
    ApiKeyRegister,
    ApiKeyUpdate,
    RateLimitRegister,
)
from server.repositories.api_client_repository import ApiClientRepository
from server.services.security.api_key_crypto import generate_api_key
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.must_be_int import must_be_int


class ApiKeyRepository:
    @classmethod
    def get_by_id(cls, *, id: int, session: Session) -> ApiKey:
        key = session.get(ApiKey, id)
        if key is None:
            raise ApiKeyNotFound(id=id)
        return key

    @classmethod
    def get_by_public_id(cls, *, public_id: str, session: Session) -> ApiKey | None:
        """Authentication hot path: one indexed lookup that also loads what
        the checks need (client status, rate limits). Returns None instead
        of raising, since an unknown key is an ordinary 401, not a 404."""
        statement = (
            select(ApiKey)
            .where(col(ApiKey.public_id) == public_id)
            .options(
                selectinload(ApiKey.client),  # type: ignore[arg-type]
                selectinload(ApiKey.rate_limits),  # type: ignore[arg-type]
            )
        )
        return session.exec(statement).first()

    @classmethod
    def get_all_by_client(cls, *, client_id: int, session: Session) -> list[ApiKey]:
        statement = (
            select(ApiKey)
            .where(col(ApiKey.client_id) == client_id)
            .order_by(col(ApiKey.created_at).desc())
        )
        return list(session.exec(statement).all())

    @classmethod
    def get_active_browser_origins(cls, *, session: Session) -> set[str]:
        """Origins of every usable browser key (not revoked, not expired,
        active client): the partner sites allowed to call us from a browser."""
        statement = (
            select(ApiKey.allowed_origins)
            .join(ApiClient, col(ApiClient.id) == col(ApiKey.client_id))
            .where(
                col(ApiKey.revoked_at).is_(None),
                col(ApiKey.expires_at) > BrazilDatetime.now_utc(),
                col(ApiClient.is_active).is_(True),
                func.cardinality(col(ApiKey.allowed_origins)) > 0,
            )
        )
        return {origin for origins in session.exec(statement) for origin in origins}

    @classmethod
    def create(
        cls,
        *,
        client_id: int,
        input: ApiKeyRegister,
        user: User,
        session: Session,
    ) -> tuple[ApiKey, str]:
        """Create a key and return it with its plaintext, which is the only
        time the plaintext exists: only its HMAC is stored."""
        client = ApiClientRepository.get_by_id(id=client_id, session=session)
        generated = generate_api_key()
        key = ApiKey(
            client_id=must_be_int(client.id),
            name=input.name,
            public_id=generated.public_id,
            key_hash=generated.key_hash,
            hash_version=generated.hash_version,
            allowed_path_prefixes=input.allowed_path_prefixes,
            allowed_origins=input.allowed_origins,
            expires_at=input.expires_at,
            created_by_id=must_be_int(user.id),
        )
        session.add(key)
        # Flush first so the key has an id for its rate limit rows.
        session.flush()
        key.rate_limits = cls.__build_rate_limits(key, input.rate_limits)
        session.flush()
        return key, generated.plaintext

    @classmethod
    def update(cls, *, id: int, input: ApiKeyUpdate, session: Session) -> ApiKey:
        key = cls.__get_not_revoked(id=id, session=session)
        key.name = input.name
        key.allowed_path_prefixes = input.allowed_path_prefixes
        key.allowed_origins = input.allowed_origins
        key.expires_at = input.expires_at
        key.updated_at = BrazilDatetime.now_utc()
        session.add(key)
        return key

    @classmethod
    def set_rate_limits(
        cls, *, id: int, limits: list[RateLimitRegister], session: Session
    ) -> ApiKey:
        """Replace all of the key's rate limits. An empty list means the
        configured defaults apply."""
        key = cls.__get_not_revoked(id=id, session=session)
        key.rate_limits.clear()
        # Flush the deletes first: the unit of work inserts before it
        # deletes, which would hit unique_api_key_rate_limit_window when a
        # window is kept with a new max.
        session.flush()
        key.rate_limits = cls.__build_rate_limits(key, limits)
        key.updated_at = BrazilDatetime.now_utc()
        session.add(key)
        session.flush()
        return key

    @classmethod
    def revoke(cls, *, id: int, reason: str, user: User, session: Session) -> ApiKey:
        """Revoke a key for good. The row stays, for the audit trail. A
        delivery link still waiting to be opened dies with it."""
        key = cls.__get_not_revoked(id=id, session=session)
        now = BrazilDatetime.now_utc()
        key.revoked_at = now
        key.revoked_by_id = must_be_int(user.id)
        key.revoked_reason = reason
        key.updated_at = now
        link = key.delivery_link
        if (
            link is not None
            and link.consumed_at is None
            and link.invalidated_at is None
        ):
            link.wipe_secret()
            link.invalidated_at = now
            link.invalidated_by_id = key.revoked_by_id
        session.add(key)
        return key

    @staticmethod
    def __build_rate_limits(
        key: ApiKey, limits: list[RateLimitRegister]
    ) -> list[ApiKeyRateLimit]:
        """Rows for an already flushed key (it needs an id)."""
        key_id = must_be_int(key.id)
        return [
            ApiKeyRateLimit(
                api_key_id=key_id,
                max_requests=limit.max_requests,
                window_seconds=limit.window_seconds,
            )
            for limit in limits
        ]

    @classmethod
    def __get_not_revoked(cls, *, id: int, session: Session) -> ApiKey:
        key = cls.get_by_id(id=id, session=session)
        if key.revoked_at is not None:
            raise ApiKeyAlreadyRevoked(id=id)
        return key


class ApiKeyNotFound(HTTPException):
    def __init__(self, id: int) -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND, f"Chave da API com id {id} não encontrada"
        )


class ApiKeyAlreadyRevoked(HTTPException):
    def __init__(self, id: int) -> None:
        super().__init__(
            status.HTTP_409_CONFLICT,
            f"A chave da API com id {id} já foi revogada e não pode ser alterada",
        )
