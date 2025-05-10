from fastapi import APIRouter, Body
from fastapi.templating import Jinja2Templates

from server.deps.authenticate import UserDep
from server.deps.owned_building_ids import OwnedBuildingIdsDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.classroom_solicitation_request_models import (
    ClassroomSolicitationApprove,
    ClassroomSolicitationDeny,
    ClassroomSolicitationRegister,
)
from server.models.http.responses.classroom_solicitation_response_models import (
    ClassroomSolicitationResponse,
)
from server.repositories.classroom_repository import ClassroomRepository
from server.repositories.classroom_solicitation_repository import (
    ClassroomSolicitationRepository,
)
from server.repositories.group_repository import GroupRepository
from server.repositories.reservation_repository import ReservationRepository
from server.repositories.user_repository import UserRepository
from server.services.email.email_service import EmailService
from server.services.security.classroom_solicitation_permission_checker import (
    ClassroomSolicitationPermissionChecker,
)
from pathlib import Path

embed = Body(..., embed=True)

router = APIRouter(prefix="/solicitations/classroom", tags=["Solicitations"])

template_path = (
    Path(__file__).resolve().parent.parent.parent / "templates" / "solicitations"
)
image_path = (
    Path(__file__).resolve().parent.parent.parent
    / "templates"
    / "assets"
    / "uspolis.logo.png"
)
templates = Jinja2Templates(directory=template_path)


@router.get("")
def get_classroom_solicitations(
    building_ids: OwnedBuildingIdsDep, session: SessionDep
) -> list[ClassroomSolicitationResponse]:
    solicitations = ClassroomSolicitationRepository.get_by_id_on_buildings_pending(
        building_ids=building_ids, session=session
    )
    return ClassroomSolicitationResponse.from_solicitation_list(solicitations)


@router.post("")
async def create_classroom_solicitation(
    input: ClassroomSolicitationRegister,
    session: SessionDep,
    user: UserDep,
) -> ClassroomSolicitationResponse:
    """Create a class reservation solicitation"""
    solicitation = ClassroomSolicitationRepository.create(
        requester=user, input=input, session=session
    )
    if solicitation.classroom_id:
        groups = GroupRepository.get_by_classroom_id(
            classroom_id=solicitation.classroom_id, session=session
        )
        users = [user for group in groups for user in group.users]
        users_set = set(users)
        users = list(users_set)
    else:
        users = UserRepository.get_all_on_building(
            building_id=input.building_id, session=session
        )
    session.commit()
    await EmailService.send_solicitation_request_email(users, solicitation)
    return ClassroomSolicitationResponse.from_solicitation(solicitation)


@router.put("/approve/{solicitation_id}")
async def approve_classroom_solicitation(
    solicitation_id: int,
    input: ClassroomSolicitationApprove,
    session: SessionDep,
    user: UserDep,
) -> ClassroomSolicitationResponse:
    """Aprove a class reservation solicitation"""
    checker = ClassroomSolicitationPermissionChecker(user, session)
    checker.check_permission(solicitation_id)
    solicitation = ClassroomSolicitationRepository.approve(
        id=solicitation_id, user=user, session=session
    )
    classroom = ClassroomRepository.get_by_id(
        id=input.classroom_id,
        session=session,
    )
    reservation = ReservationRepository.create_by_solicitation(
        creator=user,
        input=input,
        solicitation=solicitation,
        classroom=classroom,
        session=session,
    )
    solicitation.reservation = reservation
    solicitation.classroom = classroom
    session.refresh(solicitation)
    session.commit()
    await EmailService.send_solicitation_approved_email(input, solicitation)
    return ClassroomSolicitationResponse.from_solicitation(solicitation)


@router.put("/deny/{solicitation_id}")
async def deny_classroom_solicitation(
    solicitation_id: int,
    input: ClassroomSolicitationDeny,
    session: SessionDep,
    user: UserDep,
) -> ClassroomSolicitationResponse:
    """Deny a class reservation solicitation"""
    checker = ClassroomSolicitationPermissionChecker(user, session)
    checker.check_permission(solicitation_id)

    solicitation = ClassroomSolicitationRepository.deny(
        id=solicitation_id, user=user, session=session
    )
    session.commit()
    await EmailService.send_solicitation_denied_email(input, solicitation)
    return ClassroomSolicitationResponse.from_solicitation(solicitation)
