from pydantic import BaseModel
from datetime import datetime
from user_agents import parse  # type: ignore

from server.models.database.user_session_db_model import UserSession


def get_device_from_user_agent(user_agent: str) -> str:
    details = parse(user_agent)
    if details.is_pc:
        return "Desktop"
    return details.device.family  # type: ignore


class UserSessionResponse(BaseModel):
    id: str
    user_id: int
    user_email: str
    user_name: str
    user_agent: str

    browser: str
    os: str
    device: str

    ip_address: str
    expires_at: datetime
    created_at: datetime

    @staticmethod
    def from_session(session: UserSession) -> "UserSessionResponse":
        details = parse(session.user_agent)
        return UserSessionResponse(
            id=session.id,
            user_id=session.user_id,
            user_email=session.user.email,
            user_name=session.user.name,
            user_agent=session.user_agent,
            browser=details.browser.family,
            os=details.os.family,
            device=get_device_from_user_agent(session.user_agent),
            ip_address=session.ip_address,
            created_at=session.created_at,
            expires_at=session.expires_at,
        )

    @staticmethod
    def from_sessions(sessions: list[UserSession]) -> list["UserSessionResponse"]:
        return [UserSessionResponse.from_session(session) for session in sessions]
