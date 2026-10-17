from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlmodel import Session, col, select

from server.models.database.api_key_db_model import ApiKey
from server.models.database.api_key_delivery_link_db_model import ApiKeyDeliveryLink
from server.models.database.user_db_model import User
from server.services.security.api_key_link_crypto import (
    generate_link_id,
    open_sealed_api_key,
    seal_api_key,
)
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.api_key_link_status_enum import ApiKeyLinkStatus
from server.utils.must_be_int import must_be_int

INVALIDATED_REVOKE_REASON = "Link de entrega invalidado antes de ser aberto"
EXPIRED_REVOKE_REASON = "Link de entrega expirou sem ser aberto"


class ApiKeyDeliveryLinkRepository:
    """One-time delivery links (see docs/API_KEYS.md, "Entrega por link").
    A key delivered by link that nobody opened is useless, so killing the
    link (invalidation or expiry) also revokes its key."""

    @classmethod
    def get_by_id(cls, *, id: int, session: Session) -> ApiKeyDeliveryLink:
        link = session.get(ApiKeyDeliveryLink, id)
        if link is None:
            raise ApiKeyLinkNotFound()
        return link

    @classmethod
    def get_by_link_id(
        cls, *, link_id: str, session: Session, for_update: bool = False
    ) -> ApiKeyDeliveryLink:
        statement = select(ApiKeyDeliveryLink).where(
            col(ApiKeyDeliveryLink.link_id) == link_id
        )
        if for_update:
            # Locks the row until commit, so two concurrent reveals can't
            # both see it pending. populate_existing reloads an instance the
            # session already holds instead of trusting its stale state.
            statement = statement.with_for_update().execution_options(
                populate_existing=True
            )
        link = session.exec(statement).first()
        if link is None:
            raise ApiKeyLinkNotFound()
        return link

    @classmethod
    def create_for_key(
        cls,
        *,
        key: ApiKey,
        plaintext: str,
        ttl: timedelta,
        user: User,
        session: Session,
    ) -> tuple[ApiKeyDeliveryLink, str]:
        """Seal `plaintext` into a new link and return it with its token,
        the only time the token exists: it is never stored."""
        link_id = generate_link_id()
        sealed = seal_api_key(plaintext, link_id)
        now = BrazilDatetime.now_utc()
        link = ApiKeyDeliveryLink(
            api_key_id=must_be_int(key.id),
            link_id=link_id,
            ciphertext=sealed.ciphertext,
            nonce=sealed.nonce,
            salt=sealed.salt,
            expires_at=now + ttl,
            created_by_id=must_be_int(user.id),
            created_at=now,
        )
        session.add(link)
        session.flush()
        return link, sealed.token

    @classmethod
    def open(cls, *, link: ApiKeyDeliveryLink, token: str) -> str | None:
        """The sealed key if `token` opens it, without consuming the link."""
        if link.ciphertext is None or link.nonce is None or link.salt is None:
            return None
        return open_sealed_api_key(
            token=token,
            link_id=link.link_id,
            ciphertext=link.ciphertext,
            nonce=link.nonce,
            salt=link.salt,
        )

    @classmethod
    def reveal(
        cls,
        *,
        link_id: str,
        token: str,
        ip: str | None,
        user_agent: str | None,
        session: Session,
    ) -> tuple[ApiKeyDeliveryLink, str]:
        """Return the link with its key and consume it, exactly once. A wrong
        token changes nothing: link_id shows up in logs, and whoever reads
        them must not be able to burn the link."""
        link = cls.get_by_link_id(link_id=link_id, session=session, for_update=True)
        plaintext = cls.__open_pending(link, token)
        link.wipe_secret()
        link.consumed_at = BrazilDatetime.now_utc()
        link.consumed_ip = ip
        link.consumed_user_agent = user_agent[:512] if user_agent else None
        session.add(link)
        return link, plaintext

    @classmethod
    def get_pending_for_key(cls, *, key: ApiKey, token: str) -> ApiKeyDeliveryLink:
        """The key's link, checking it is still pending and that `token`
        opens it, without consuming it (e.g. before emailing the link)."""
        link = key.delivery_link
        if link is None:
            raise ApiKeyLinkNotFound()
        cls.__open_pending(link, token)
        return link

    @classmethod
    def mark_emailed(
        cls, *, link: ApiKeyDeliveryLink, to: list[str], user: User, session: Session
    ) -> ApiKeyDeliveryLink:
        link.emailed_at = BrazilDatetime.now_utc()
        link.emailed_to = ", ".join(to)
        link.emailed_by_id = must_be_int(user.id)
        session.add(link)
        return link

    @classmethod
    def invalidate(cls, *, id: int, user: User, session: Session) -> ApiKeyDeliveryLink:
        link = cls.get_by_id(id=id, session=session)
        if link.consumed_at is not None or link.invalidated_at is not None:
            raise ApiKeyLinkGone()
        cls.__kill(
            link,
            now=BrazilDatetime.now_utc(),
            user_id=must_be_int(user.id),
            reason=INVALIDATED_REVOKE_REASON,
        )
        session.add(link)
        return link

    @classmethod
    def expire_pending(
        cls, *, now: datetime, session: Session
    ) -> list[ApiKeyDeliveryLink]:
        """Wipe and kill links that expired unopened. Reveal already checks
        expiry itself, so this is only cleanup: it removes the sealed keys
        from the database and revokes the keys nobody received."""
        statement = select(ApiKeyDeliveryLink).where(
            col(ApiKeyDeliveryLink.expires_at) <= now,
            col(ApiKeyDeliveryLink.consumed_at).is_(None),
            col(ApiKeyDeliveryLink.invalidated_at).is_(None),
        )
        links = list(session.exec(statement).all())
        for link in links:
            cls.__kill(link, now=now, user_id=None, reason=EXPIRED_REVOKE_REASON)
            session.add(link)
        return links

    @classmethod
    def __open_pending(cls, link: ApiKeyDeliveryLink, token: str) -> str:
        if link.status() != ApiKeyLinkStatus.PENDING or not link.api_key.is_usable():
            raise ApiKeyLinkGone()
        plaintext = cls.open(link=link, token=token)
        if plaintext is None:
            raise ApiKeyLinkNotFound()
        return plaintext

    @staticmethod
    def __kill(
        link: ApiKeyDeliveryLink, *, now: datetime, user_id: int | None, reason: str
    ) -> None:
        link.wipe_secret()
        link.invalidated_at = now
        link.invalidated_by_id = user_id
        key = link.api_key
        if key.revoked_at is None:
            key.revoked_at = now
            key.revoked_by_id = user_id
            key.revoked_reason = reason
            key.updated_at = now


class ApiKeyLinkNotFound(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND, "Link de entrega de chave não encontrado"
        )


class ApiKeyLinkGone(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status.HTTP_410_GONE,
            "Este link de entrega já foi usado, expirou ou foi invalidado",
        )
