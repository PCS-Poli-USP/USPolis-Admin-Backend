from fastapi import Request

from server.config import CONFIG
from server.deps.session_dep import SessionDep
from server.models.database.user_db_model import User
from server.repositories.users_repository import UserRepository


async def authenticate_mock(request: Request, session: SessionDep) -> User:
    username: str = CONFIG.mock_username
    user: User = UserRepository.get_by_username(username=username, session=session)
    request.state.current_user = user
    return user
