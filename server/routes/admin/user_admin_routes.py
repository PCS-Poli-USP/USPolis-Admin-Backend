from fastapi import APIRouter, Body, HTTPException

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.user_request_models import UserRegister, UserUpdate
from server.models.http.responses.user_response_models import (
    UseCoreResponse,
    UserPermissionResponse,
    UserResponse,
)
from server.repositories.user_repository import UserRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model_by_alias=False)
def get_users(session: SessionDep) -> list[UseCoreResponse]:
    """Get all users"""
    users = UserRepository.get_all(session=session)
    return UseCoreResponse.core_from_user_list(users)


@router.get("/permissions")
def get_users_permissions(session: SessionDep) -> list[UserPermissionResponse]:
    """Get all users with permissions and roles"""
    users = UserRepository.get_all_with_permissions(session=session)
    return UserPermissionResponse.from_user_list(users)


@router.get("/permissions/{user_id}")
def get_user_permissions(user_id: int, session: SessionDep) -> UserPermissionResponse:
    """Get user with permissions and roles"""
    user = UserRepository.get_with_permissions(user_id=user_id, session=session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserPermissionResponse.from_user(user)


@router.post("")
def create_user(
    input: UserRegister,
    user: UserDep,
    session: SessionDep,
) -> UserResponse:
    """Create new user."""
    new_user = UserRepository.create(
        creator=user,
        input=input,
        session=session,
    )
    session.commit()
    session.refresh(new_user)
    return UserResponse.from_user(new_user)


@router.put("/{user_id}")
def update_user(
    user_id: int,
    input: UserUpdate,
    current_user: UserDep,
    session: SessionDep,
) -> UserResponse:
    """Update a user by id"""
    updated = UserRepository.update(
        requester=current_user, id=user_id, input=input, session=session
    )
    session.commit()
    session.refresh(updated)
    return UserResponse.from_user(updated)
