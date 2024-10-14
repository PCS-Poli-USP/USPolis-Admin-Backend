from fastapi import APIRouter

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.database.user_db_model import User
from server.models.http.responses.user_response_models import UserResponse
from server.repositories.user_repository import UserRepository

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("")
async def get_current_user(
    user: UserDep,
) -> UserResponse:
    """Get current user"""
    return UserResponse.from_user(user)


@router.get("/{building_id}")
async def get_users_on_building(building_id: int, session: SessionDep) -> list[User]:
    """Get users on building"""
    users = UserRepository.get_all_on_building(
        building_id=building_id, session=session)
    return users
