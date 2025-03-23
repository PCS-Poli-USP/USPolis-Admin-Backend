from datetime import datetime

from fastapi import APIRouter, Body, HTTPException, Response

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.user_request_models import UserRegister, UserUpdate
from server.models.http.responses.generic_responses import NoContent
from server.models.http.responses.user_response_models import UserResponse
from server.repositories.building_repository import BuildingRepository
from server.repositories.user_repository import UserRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model_by_alias=False)
def get_users(session: SessionDep) -> list[UserResponse]:
    """Get all users"""
    users = UserRepository.get_all(session=session)
    return UserResponse.from_user_list(users)


@router.post("")
def create_user(
    user_input: UserRegister,
    user: UserDep,
    session: SessionDep,
) -> UserResponse:
    """Create new user."""
    new_user = UserRepository.create(
        creator=user,
        user_in=user_input,
        session=session,
    )
    session.refresh(new_user)
    return UserResponse.from_user(new_user)


@router.put("/{user_id}")
def update_user(
    user_id: int,
    user_input: UserUpdate,
    current_user: UserDep,
    session: SessionDep,
) -> UserResponse:
    """Update a user by id"""
    user_to_update = UserRepository.get_by_id(user_id=user_id, session=session)

    if user_id == current_user.id:
        if current_user.is_admin != user_input.is_admin:
            raise HTTPException(400, "Não pode editar seu próprio status de admin")

    buildings = []
    if user_input.building_ids is not None:
        buildings = BuildingRepository.get_by_ids(
            ids=user_input.building_ids, session=session
        )

    user_to_update.buildings = buildings
    user_to_update.is_admin = user_input.is_admin
    user_to_update.updated_at = datetime.now()
    UserRepository.update(user=user_to_update, session=session)
    return UserResponse.from_user(user_to_update)


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: UserDep,
    session: SessionDep,
) -> Response:
    """Delete a user by id"""
    if current_user.id == user_id:
        raise HTTPException(400, "Não pode remover seu próprio usuário")

    UserRepository.delete(user_id=user_id, session=session)
    return NoContent
