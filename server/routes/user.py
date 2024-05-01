from datetime import datetime

from fastapi import APIRouter, Body

from server.models.user import User, UserRegister

router = APIRouter(prefix="/users", tags=["Users"])

embed = Body(..., embed=True)

@router.post("")
async def create_user(user_input: UserRegister) -> User:
    """Create new user."""
    new_user = User(
        buildings=None,
        cognito_id="x",
        created_by=None,
        email=user_input.email,
        is_admin=user_input.is_admin,
        name=user_input.name,
        username=user_input.username,
        updated_at=datetime.now()
    )
    await new_user.create()
    return new_user