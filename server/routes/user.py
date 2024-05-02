from datetime import datetime

from fastapi import APIRouter, Body, Depends, HTTPException

from server.models.user import User, UserRegister, UserUpdate
from server.services.auth.cognito import (
    create_cognito_user,
    delete_cognito_user,
    get_current_admin_user,
)
from server.services.queries.building.get_buildings_by_ids import get_buildings_by_ids
from server.services.queries.user.get_user_by_id import get_user_by_id

router = APIRouter(prefix="/users", tags=["Users"])

embed = Body(..., embed=True)


@router.post("")
async def create_user(
    user_input: UserRegister, user: User = Depends(get_current_admin_user)
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


@router.put("/{user_id}")
async def update_user(
    user_id: str,
    user_input: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
) -> str:
    user_to_update = await get_user_by_id(user_id)

    if user_id == current_user.id:
        if current_user.is_admin != user_input.is_admin:
            raise HTTPException(400, "Cannot edit own admin status")

    buildings = None
    if user_input.buildings is not None:
        buildings = await get_buildings_by_ids(user_input.buildings)
    user_to_update.buildings = buildings
    user_to_update.is_admin = user_input.is_admin
    user_to_update.name = user_input.name
    user_to_update.updated_at = datetime.now()
    await user_to_update.save()
    return str(user_to_update.id)


@router.delete("/{user_id}")
async def delete_user(
    user_id: str, current_user: User = Depends(get_current_admin_user)
) -> int:
    user_to_delete = await get_user_by_id(user_id)
    if current_user.id == user_to_delete.id:
        raise HTTPException(400, "Cannot delete self")

    delete_cognito_user(user_to_delete.username)
    x = await user_to_delete.delete()
    if x is None:
        raise HTTPException(500, "No user deleted")
    return x.deleted_count
