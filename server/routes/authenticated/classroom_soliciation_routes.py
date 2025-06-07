from fastapi import APIRouter, Body
from fastapi.templating import Jinja2Templates

from server.deps.authenticate import UserDep
from server.deps.owned_building_ids import OwnedBuildingIdsDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.classroom_solicitation_request_models import (
    ClassroomSolicitationRegister,
)
from server.models.http.responses.classroom_solicitation_response_models import (
    ClassroomSolicitationResponse,
)
from server.repositories.classroom_solicitation_repository import (
    ClassroomSolicitationRepository,
)
from server.repositories.group_repository import GroupRepository
from server.repositories.user_repository import UserRepository
from server.services.email.email_service import EmailService
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


@router.get("/pending")
async def get_pending_classroom_solicitations(
    building_ids: OwnedBuildingIdsDep, session: SessionDep
) -> list[ClassroomSolicitationResponse]:
    solicitations = ClassroomSolicitationRepository.get_pending_by_buildings_ids(
        building_ids=building_ids, session=session
    )
    return ClassroomSolicitationResponse.from_solicitation_list(solicitations)


@router.get("")
async def get_all_classroom_solicitations(
    building_ids: OwnedBuildingIdsDep,
    session: SessionDep,
) -> list[ClassroomSolicitationResponse]:
    solicitations = ClassroomSolicitationRepository.get_by_buildings_ids(
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
