from fastapi import APIRouter

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.deps.repository_adapters.building_repository_adapter import (
    BuildingRespositoryAdapterDep,
)
from server.deps.repository_adapters.classroom_repository_adapter import (
    ClassroomRepositoryDep,
)

from server.models.database.user_db_model import User
from server.models.http.responses.classroom_response_models import ClassroomResponse
from server.models.http.responses.user_response_models import UserResponse
from server.models.http.responses.building_response_models import BuildingResponse
from server.repositories.user_repository import UserRepository


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("")
async def get_current_user(
    user: UserDep,
) -> UserResponse:
    """Get current user"""
    return UserResponse.from_user(user)


@router.get("/my-buildings")
async def get_my_buildings(
    repository: BuildingRespositoryAdapterDep,
) -> list[BuildingResponse]:
    """Get all buildings for authenticated user"""
    buildings = repository.get_all()
    return BuildingResponse.from_building_list(buildings)


@router.get("/my-classrooms")
async def get_my_classrooms(
    repository: ClassroomRepositoryDep,
) -> list[ClassroomResponse]:
    """Get all classrooms for authenticated user"""
    classrooms = repository.get_all()
    return ClassroomResponse.from_classroom_list(classrooms)


@router.get("/{building_id}")
async def get_users_on_building(building_id: int, session: SessionDep) -> list[User]:
    """Get users on building"""
    users = UserRepository.get_all_on_building(building_id=building_id, session=session)
    return users
