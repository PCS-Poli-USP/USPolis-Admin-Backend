from datetime import datetime

from fastapi import APIRouter, Body

from server.models.user_building import User, UserRegister

router = APIRouter(prefix="/users", tags=["Users"])

embed = Body(..., embed=True)

@router.post("")
async def create_user(user_input: UserRegister) -> User:
    """Create new user."""
    new_user = User(
        buildings=None,
        cognito_id="x",
        created_by=None,
        email="x.com",
        is_admin=True,
        name="Henrique Duran",
        username="hfduran",
        updated_at=datetime.now()
    )
    await new_user.create()
    return new_user