from datetime import datetime

from server.models.database.user_db_model import User
from server.config import CONFIG


def make_admin_user(username: str) -> User:
    user = User(
        username=username,
        name=f"Admin {username}",
        email=f"{username}@admin.com",
        is_admin=True,
        cognito_id=f"{username}-cognito-id",
        updated_at=datetime.now()
    )
    return user


async def add_admin_user(username) -> str:
    user = await User.by_username(username)
    if user:
        return str(user.id)
    user = make_admin_user(username)
    await user.create()
    return str(user.id)


async def get_test_admin_user() -> User:
    if await User.check_username_exists(CONFIG.mock_username):
        return await User.by_username(CONFIG.mock_username)
    user = make_admin_user(CONFIG.mock_username)
    await user.create()
    return user


async def add_empty_user() -> str:
    pass
