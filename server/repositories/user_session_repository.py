from datetime import timedelta
from fastapi import HTTPException, status
from sqlmodel import Session, col, select
from sqlalchemy.exc import NoResultFound

from server.models.database.user_session_db_model import UserSession
from server.utils.brazil_datetime import BrazilDatetime


SESSION_DURATION_DAYS = 30


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
        user_session = UserSession(
            user_id=user_id,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=BrazilDatetime.now_utc() + timedelta(days=SESSION_DURATION_DAYS),
        )
        session.add(user_session)
        return user_session

    @staticmethod
    def get_session(
        *,
        user_id: int,
        user_agent: str,
        ip_address: str,
        session: Session,
    ) -> UserSession | None:
        statement = select(UserSession).where(
            col(UserSession.user_id) == user_id,
            col(UserSession.user_agent) == user_agent,
            col(UserSession.ip_address) == ip_address,
        )
        return session.exec(statement).first()

    @staticmethod
    def extend_session(*, user_session: UserSession, session: Session) -> None:
        user_session.expires_at = BrazilDatetime.now_utc() + timedelta(
            days=SESSION_DURATION_DAYS
        )
        session.add(user_session)

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
