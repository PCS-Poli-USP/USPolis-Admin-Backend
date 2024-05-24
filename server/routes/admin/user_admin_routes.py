from datetime import datetime

from fastapi import APIRouter, Body, HTTPException

from server.deps.authenticate import UserDep
from server.deps.cognito_client import CognitoClientDep
from server.deps.session_dep import SessionDep
from server.models.database.user_db_model import User
from server.models.http.requests.user_request_models import UserRegister, UserUpdate
from server.models.http.responses.user_response_models import UserResponse
from server.repositories.buildings_repository import BuildingRepository
from server.repositories.users_repository import UserRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model_by_alias=False)
async def get_users(session: SessionDep) -> list[UserResponse]:
    users = UserRepository.get_all(session=session)
    return await UserResponse.from_user_list(users)


@router.post("")
async def create_user(
    user_input: UserRegister,
    user: UserDep,
    session: SessionDep,
    cognito_client: CognitoClientDep,
) -> User:
    """Create new user."""
    new_user = UserRepository.create(
        creator=user,
        user_in=user_input,
        cognito_client=cognito_client,
        session=session,
    )
    session.refresh(new_user)
    return new_user


@router.put("/{user_id}")
async def update_user(
    user_id: str,
    user_input: UserUpdate,
    current_user: UserDep,
    session: SessionDep,
) -> User:
    user_to_update = UserRepository.get_by_id(user_id=user_id, session=session)

    if user_id == current_user.id:  # type: ignore [comparison-overlap]
        if current_user.is_admin != user_input.is_admin:
            raise HTTPException(400, "Cannot edit own admin status")

    buildings = None
    if user_input.building_ids is not None:
        buildings = BuildingRepository.get_by_ids(
            ids=user_input.building_ids, session=session
        )

    user_to_update.buildings = buildings
    user_to_update.is_admin = user_input.is_admin
    user_to_update.updated_at = datetime.now()
    UserRepository.update(user=user_to_update, session=session)
    return user_to_update


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: UserDep,
    session: SessionDep,
    cognito_client: CognitoClientDep,
) -> None:
    if current_user.id == user_id:  # type: ignore [comparison-overlap]
        raise HTTPException(400, "Cannot delete self")

    UserRepository.delete(
        user_id=user_id, session=session, cognito_client=cognito_client
    )
