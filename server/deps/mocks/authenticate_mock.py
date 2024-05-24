from fastapi import Request
from sqlmodel import Session

from server.config import CONFIG
from server.db import engine
from server.models.database.user_db_model import User
from server.repositories.users_repository import UserRepository


async def authenticate_mock(
    request: Request,
) -> User:
    username: str = CONFIG.mock_username
    with Session(engine) as session:
        user: User = UserRepository.get_by_username(username=username, session=session)
    request.state.current_user = user
    return user
