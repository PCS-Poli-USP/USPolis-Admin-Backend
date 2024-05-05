from fastapi import HTTPException, Request, status

from server.config import CONFIG
from server.models.database.user_db_model import User


async def authenticate_mock(
    request: Request,
) -> User:
    username: str = CONFIG.mock_username
    user: User | None = await User.by_username(username)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    request.state.current_user = user
    return user
