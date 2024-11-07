from fastapi import Request

from server.config import CONFIG
from server.deps.session_dep import SessionDep
from server.models.database.user_db_model import User
from server.repositories.user_repository import UserRepository


async def authenticate_mock(request: Request, session: SessionDep) -> User:
    email: str = CONFIG.mock_email
    user: User = UserRepository.get_by_email(email=email, session=session)
    request.state.current_user = user
    return user
