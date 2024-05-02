from fastapi import HTTPException
from server.models.user import User


async def get_user_by_id(user_id: str) -> User:
    user = await User.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
