from fastapi import APIRouter, Request

from server.deps.authenticate import UserDep
from server.deps.repository_adapters.class_repository_adapter import (
    ClassRepositoryDep,
)
from server.deps.repository_adapters.reservation_repository_adapter import (
    ReservationRepositoryDep,
)
from server.deps.repository_adapters.subject_repository_adapter import (
    SubjectRepositoryDep,
)
from server.deps.session_dep import SessionDep
from server.deps.repository_adapters.building_repository_adapter import (
    BuildingRepositoryDep,
)
from server.deps.repository_adapters.classroom_repository_adapter import (
    ClassroomRepositoryDep,
)

from server.models.database.user_db_model import User
from server.models.http.responses.class_response_models import ClassResponse
from server.models.http.responses.classroom_response_models import ClassroomResponse
from server.models.http.responses.classroom_solicitation_response_models import (
    ClassroomSolicitationResponse,
)
from server.models.http.responses.reservation_response_models import ReservationResponse
from server.models.http.responses.subject_response_models import SubjectResponse
from server.models.http.responses.user_response_models import UserResponse
from server.models.http.responses.building_response_models import BuildingResponse
from server.repositories.classroom_solicitation_repository import (
    ClassroomSolicitationRepository,
)
from server.repositories.user_repository import UserRepository


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("")
def get_current_user(
    request: Request,
    session: SessionDep,
    user: UserDep,
) -> UserResponse:
    """Get current user"""
    UserRepository.visit_user(user=user, session=session)
    session.commit()
    response = UserResponse.from_user(user)
    if hasattr(request.state, "user_info"):
        response.user_info = request.state.user_info
    else:
        response.user_info = None
    return response


@router.get("/my-buildings")
def get_my_buildings(
    repository: BuildingRepositoryDep,
) -> list[BuildingResponse]:
    """Get all buildings for authenticated user"""
    buildings = repository.get_all()
    return BuildingResponse.from_building_list(buildings)


@router.get("/my-subjects")
def get_my_subjects(
    repository: SubjectRepositoryDep,
) -> list[SubjectResponse]:
    """Get all subjects for authenticated user"""
    subjects = repository.get_all()
    return SubjectResponse.from_subject_list(subjects)


@router.get("/my-classes")
def get_my_classes(
    repository: ClassRepositoryDep,
) -> list[ClassResponse]:
    """Get all classes for authenticated user"""
    classes = repository.get_all()
    return ClassResponse.from_class_list(classes)


@router.get("/my-classrooms")
def get_my_classrooms(
    repository: ClassroomRepositoryDep,
) -> list[ClassroomResponse]:
    """Get all classrooms for authenticated user"""
    classrooms = repository.get_all()
    return ClassroomResponse.from_classroom_list(classrooms)


@router.get("/my-reservations")
def get_my_reservations(
    repository: ReservationRepositoryDep,
) -> list[ReservationResponse]:
    """Get all reservations for authenticated user"""
    reservations = repository.get_all()
    return ReservationResponse.from_reservation_list(reservations)


@router.get("/my-solicitations")
def get_my_solicitaions(
    user: UserDep,
    session: SessionDep,
) -> list[ClassroomSolicitationResponse]:
    """Get all solicitations for authenticated user"""
    solicitations = ClassroomSolicitationRepository.get_by_user(user, session)
    return ClassroomSolicitationResponse.from_solicitation_list(solicitations)


@router.get("/{building_id}")
def get_users_on_building(building_id: int, session: SessionDep) -> list[User]:
    """Get users on building"""
    users = UserRepository.get_all_on_building(building_id=building_id, session=session)
    return users
