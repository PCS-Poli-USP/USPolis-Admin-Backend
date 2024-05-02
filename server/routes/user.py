from datetime import datetime

from fastapi import APIRouter, Body, Depends

from server.models.user import User, UserRegister
from server.services.auth.cognito import create_cognito_user, current_user
from server.services.queries.building.get_buildings_by_ids import get_buildings_by_ids

router = APIRouter(prefix="/users", tags=["Users"])

embed = Body(..., embed=True)


@router.post("")
async def create_user(
    user_input: UserRegister, user: User = Depends(current_user)
) -> str:
    """Create new user."""

    buildings = None
    if user_input.buildings is not None:
        buildings = get_buildings_by_ids(user_input.buildings)

    cognito_id = create_cognito_user(user_input.username, user_input.email)

    new_user = User(
        buildings=buildings,  # type: ignore [arg-type]
        cognito_id=cognito_id,
        created_by=user,
        email=user_input.email,
        is_admin=user_input.is_admin,
        name=user_input.name,
        username=user_input.username,
        updated_at=datetime.now(),
    )
    await new_user.create()
    return str(new_user.id)
