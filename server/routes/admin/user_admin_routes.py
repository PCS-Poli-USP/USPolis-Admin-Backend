from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import JSONResponse

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.user_request_models import UserRegister, UserUpdate
from server.models.http.responses.user_response_models import UserResponse
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


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: UserDep,
    session: SessionDep,
) -> JSONResponse:
    """Delete a user by id"""
    if current_user.id == user_id:
        raise HTTPException(400, "Não pode remover seu próprio usuário")

    UserRepository.delete(user_id=user_id, session=session)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Usuário removido com sucesso",
        },
    )
