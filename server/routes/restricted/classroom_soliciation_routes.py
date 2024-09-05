from fastapi import APIRouter, Body

from server.deps.authenticate import UserDep
from server.deps.owned_building_ids import OwnedBuildingIdsDep
from server.deps.session_dep import SessionDep
from server.models.http.responses.classroom_solicitation_response_models import (
    ClassroomSolicitationResponse,
)
from server.repositories.classroom_solicitation_repository import (
    ClassroomSolicitationRepository,
)
from server.repositories.reservation_repository import ReservationRepository
from server.services.security.classroom_solicitation_permission_checker import (
    classroom_solicitation_permission_checker,
)

embed = Body(..., embed=True)

router = APIRouter(prefix="/solicitations/classroom", tags=["Solicitations"])


@router.get("")
def get_classroom_solicitations(
    building_ids: OwnedBuildingIdsDep, session: SessionDep
) -> list[ClassroomSolicitationResponse]:
    solicitations = ClassroomSolicitationRepository.get_by_id_on_buildings(
        building_ids=building_ids, session=session
    )
    return ClassroomSolicitationResponse.from_solicitation_list(solicitations)


@router.put("/approve/{solicitation_id}")
def aprove_classroom_solicitation(
    solicitation_id: int,
    session: SessionDep,
    user: UserDep,
) -> ClassroomSolicitationResponse:
    """Aprove a class reservation solicitation"""
    classroom_solicitation_permission_checker(user, solicitation_id, session)
    solicitation = ClassroomSolicitationRepository.approve(
        id=solicitation_id, session=session
    )
    ReservationRepository.create_by_solicitation(
        creator=user, solicitation=solicitation, session=session
    )
    session.commit()
    return ClassroomSolicitationResponse.from_solicitation(solicitation)


@router.put("/deny/{solicitation_id}")
def deny_classroom_solicitation(
    solicitation_id: int, session: SessionDep, user: UserDep
) -> ClassroomSolicitationResponse:
    """Deny a class reservation solicitation"""
    classroom_solicitation_permission_checker(user, solicitation_id, session)
    solicitation = ClassroomSolicitationRepository.deny(
        id=solicitation_id, session=session
    )
    session.commit()
    return ClassroomSolicitationResponse.from_solicitation(solicitation)
