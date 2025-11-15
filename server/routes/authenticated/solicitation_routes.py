import asyncio

from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from server.deps.authenticate import UserDep
from server.deps.owned_building_ids import OwnedBuildingIdsDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.solicitation_request_models import (
    SolicitationRegister,
)
from server.models.http.responses.solicitation_response_models import (
    SolicitationResponse,
)
from server.repositories.solicitation_repository import (
    SolicitationRepository,
)
from server.services.email.email_service import EmailService
from pathlib import Path

embed = Body(..., embed=True)

router = APIRouter(prefix="/solicitations", tags=["Solicitations"])

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
def get_all_solicitations(
    building_ids: OwnedBuildingIdsDep,
    session: SessionDep,
) -> list[SolicitationResponse]:
    solicitations = SolicitationRepository.get_by_buildings_ids(
        building_ids=building_ids, session=session
    )
    return SolicitationResponse.from_solicitation_list(solicitations)


@router.get("/pending")
async def get_pending_solicitations(
    building_ids: OwnedBuildingIdsDep, session: SessionDep
) -> list[SolicitationResponse]:
    solicitations = SolicitationRepository.get_pending_by_buildings_ids(
        building_ids=building_ids, session=session
    )
    return SolicitationResponse.from_solicitation_list(solicitations)


@router.patch("/cancel/{solicitation_id}")
async def cancel_solicitation(
    solicitation_id: int, user: UserDep, session: SessionDep
) -> JSONResponse:
    """Cancel a class reservation solicitation"""
    solicitation = SolicitationRepository.cancel(
        id=solicitation_id, user=user, session=session
    )
    session.commit()
    users = solicitation.get_administrative_users_for_email()
    asyncio.create_task(
        EmailService.send_solicitation_cancelled_email(users, solicitation)
    )
    return JSONResponse(
        status_code=200,
        content={"message": "Solicitaçao cancelada com sucesso."},
    )


@router.post("")
async def create_solicitation(
    input: SolicitationRegister,
    session: SessionDep,
    user: UserDep,
) -> SolicitationResponse:
    """Create a class reservation solicitation"""
    solicitation = SolicitationRepository.create(
        requester=user, input=input, session=session
    )
    users = solicitation.get_administrative_users_for_email()
    session.commit()
    asyncio.create_task(
        EmailService.send_solicitation_request_email(users, solicitation)
    )
    return SolicitationResponse.from_solicitation(solicitation)
