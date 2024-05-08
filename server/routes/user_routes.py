from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException

from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User
from server.models.http.requests.user_request_models import UserRegister, UserUpdate
from server.services.auth.authenticate import admin_authenticate
from server.services.cognito.cognito_client import CognitoClient

embed = Body(..., embed=True)

router = APIRouter(
    prefix="/users", tags=["Users"], dependencies=[Depends(admin_authenticate)]
)


@router.post("")
async def create_user(
    user_input: UserRegister,
    user: Annotated[User, Depends(admin_authenticate)],
    cognito_client: Annotated[CognitoClient, Depends()],
) -> str:
    """Create new user."""

    buildings = None
    if user_input.buildings is not None:
        buildings = await Building.by_ids(user_input.buildings)

    cognito_id = cognito_client.create_user(user_input.username, user_input.email)

    new_user = User(
        buildings=buildings, # type: ignore
        cognito_id=cognito_id,
        created_by=user, # type: ignore
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
    current_user: Annotated[User, Depends(admin_authenticate)],
) -> str:
    user_to_update = await User.by_id(user_id)

    if user_id == current_user.id:
        if current_user.is_admin != user_input.is_admin:
            raise HTTPException(400, "Cannot edit own admin status")

    buildings = None
    if user_input.buildings is not None:
        buildings = await Building.by_ids(user_input.buildings)
    user_to_update.buildings = buildings # type: ignore
    user_to_update.is_admin = user_input.is_admin
    user_to_update.name = user_input.name
    user_to_update.updated_at = datetime.now()
    await user_to_update.save() # type: ignore
    return str(user_to_update.id)


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: Annotated[User, Depends(admin_authenticate)],
    cognito_client: Annotated[CognitoClient, Depends()],
) -> int:
    user_to_delete = await User.by_id(user_id)
    if current_user.id == user_to_delete.id:
        raise HTTPException(400, "Cannot delete self")

    cognito_client.delete_user(user_to_delete.username)
    response = await user_to_delete.delete() # type: ignore
    if response is None:
        raise HTTPException(500, "No user deleted")
    return int(response.deleted_count)
