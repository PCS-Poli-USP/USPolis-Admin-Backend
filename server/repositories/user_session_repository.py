from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlmodel import Session, col, select
from sqlalchemy.exc import NoResultFound

from server.models.database.user_session_db_model import UserSession
from server.utils.brazil_datetime import BrazilDatetime


SESSION_DURATION_DAYS = 30
# Absolute cap on total session lifetime since creation, regardless of
# renewals. See SESSION_MANAGEMENT.md for the full rationale.
SESSION_MAX_AGE_DAYS = 90


class UserSessionRepository:
    @staticmethod
    def get_session_by_id(*, id: str, session: Session) -> UserSession:
        statement = select(UserSession).where(col(UserSession.id) == id)
        try:
            user_session = session.exec(statement).one()
        except NoResultFound:
            raise UserSessionNotFound()
        return user_session

    @staticmethod
    def get_session_opt(*, id: str, session: Session) -> UserSession | None:
        return session.get(UserSession, id)

    @staticmethod
    def get_all_sessions(*, session: Session) -> list[UserSession]:
        statement = select(UserSession)
        return list(session.exec(statement).all())

    @staticmethod
    def get_all_sessions_by_user_id(
        *, user_id: int, session: Session
    ) -> list[UserSession]:
        statement = select(UserSession).where(col(UserSession.user_id) == user_id)
        return list(session.exec(statement).all())

    @staticmethod
    def create_session(
        *,
        user_id: int,
        user_agent: str,
        ip_address: str,
        session: Session,
    ) -> UserSession:
        now = BrazilDatetime.now_utc()
        user_session = UserSession(
            user_id=user_id,
            user_agent=user_agent,
            ip_address=ip_address,
            created_at=now,
            expires_at=UserSessionRepository._capped_expiry(created_at=now),
        )
        session.add(user_session)
        return user_session

    @staticmethod
    def get_session(
        *,
        user_id: int,
        user_agent: str,
        session: Session,
    ) -> UserSession | None:
        """Matches on (user_id, user_agent) only - not ip_address, which
        changes too often (VPNs, university/carrier NAT subnets) to be a
        useful part of session identity. See SESSION_MANAGEMENT.md."""
        statement = select(UserSession).where(
            col(UserSession.user_id) == user_id,
            col(UserSession.user_agent) == user_agent,
        )
        return session.exec(statement).first()

    @staticmethod
    def _capped_expiry(*, created_at: datetime) -> datetime:
        sliding_expiry = BrazilDatetime.now_utc() + timedelta(days=SESSION_DURATION_DAYS)
        hard_cap = created_at + timedelta(days=SESSION_MAX_AGE_DAYS)
        return min(sliding_expiry, hard_cap)

    @staticmethod
    def has_reached_max_age(*, user_session: UserSession) -> bool:
        return BrazilDatetime.now_utc() >= user_session.created_at + timedelta(
            days=SESSION_MAX_AGE_DAYS
        )

    @staticmethod
    def extend_session(*, user_session: UserSession, session: Session) -> None:
        user_session.expires_at = UserSessionRepository._capped_expiry(
            created_at=user_session.created_at
        )
        session.add(user_session)

    @staticmethod
    def start_or_renew_session(
        *,
        user_id: int,
        user_agent: str,
        ip_address: str,
        session: Session,
    ) -> UserSession:
        """Used only by the interactive login flow (`/auth/get-tokens`). A
        session that already `has_reached_max_age` is discarded and replaced
        with a fresh one instead of extended - see SESSION_MANAGEMENT.md for
        why this is the only path allowed to reset the absolute cap."""
        existing = UserSessionRepository.get_session(
            user_id=user_id,
            user_agent=user_agent,
            session=session,
        )
        if existing and UserSessionRepository.has_reached_max_age(
            user_session=existing
        ):
            session.delete(existing)
            existing = None

        if existing:
            UserSessionRepository.extend_session(user_session=existing, session=session)
            return existing

        return UserSessionRepository.create_session(
            user_id=user_id,
            user_agent=user_agent,
            ip_address=ip_address,
            session=session,
        )

    @staticmethod
    def get_valid_session_for_renewal(
        *, session_id: str, user_id: int, session: Session
    ) -> UserSession | None:
        """Used by the interactive login flow (`/auth/get-tokens`) to check
        whether the browser already carries a live session cookie for this
        user before falling back to the user_agent-based lookup in
        start_or_renew_session. A session belonging to a different user (e.g.
        a shared browser previously logged in as someone else), an expired
        one, or one that has reached the absolute max age is not reusable -
        the max-age case is deleted outright, matching the reset-on-real-login
        behavior documented in SESSION_MANAGEMENT.md."""
        user_session = UserSessionRepository.get_session_opt(
            id=session_id, session=session
        )
        if user_session is None or user_session.user_id != user_id:
            return None
        if user_session.is_expired():
            return None
        if UserSessionRepository.has_reached_max_age(user_session=user_session):
            session.delete(user_session)
            return None
        return user_session

    @staticmethod
    def delete_session(*, session_id: str, session: Session) -> None:
        user_session = UserSessionRepository.get_session_by_id(
            id=session_id, session=session
        )
        session.delete(user_session)

    @staticmethod
    def delete_all_sessions_by_user_id(*, user_id: int, session: Session) -> None:
        sessions = UserSessionRepository.get_all_sessions_by_user_id(
            user_id=user_id, session=session
        )
        for user_session in sessions:
            session.delete(user_session)


class UserSessionNotFound(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão de usuário não encontrada",
        )
