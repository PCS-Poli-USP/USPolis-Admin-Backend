from fastapi import APIRouter, BackgroundTasks, Body, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import time

from server.deps.authenticate import UserDep
from server.deps.owned_building_ids import OwnedBuildingIdsDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.classroom_solicitation_request_models import (
    ClassroomSolicitationApprove,
    ClassroomSolicitationDeny,
    ClassroomSolicitationRegister,
)
from server.models.http.requests.email_request_models import (
    SolicitationApprovedMail,
    SolicitationDeniedMail,
    SolicitationRequestedMail,
)
from server.models.http.responses.classroom_solicitation_response_models import (
    ClassroomSolicitationResponse,
)
from server.repositories.classroom_repository import ClassroomRepository
from server.repositories.classroom_solicitation_repository import (
    ClassroomSolicitationRepository,
)
from server.repositories.reservation_repository import ReservationRepository
from server.services.email.email_service import EmailService
from server.services.security.classroom_solicitation_permission_checker import (
    classroom_solicitation_permission_checker,
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
    solicitations = ClassroomSolicitationRepository.get_by_id_on_buildings(
        building_ids=building_ids, session=session
    )
    return ClassroomSolicitationResponse.from_solicitation_list(solicitations)


@router.post("")
def create_classroom_solicitation(
    input: ClassroomSolicitationRegister, session: SessionDep, user: UserDep
) -> ClassroomSolicitationResponse:
    """Create a class reservation solicitation"""
    solicitation = ClassroomSolicitationRepository.create(
        requester=user, input=input, session=session
    )
    session.commit()
    return ClassroomSolicitationResponse.from_solicitation(solicitation)


@router.put("/approve/{solicitation_id}")
def approve_classroom_solicitation(
    solicitation_id: int,
    input: ClassroomSolicitationApprove,
    session: SessionDep,
    user: UserDep,
    background_tasks: BackgroundTasks,
) -> ClassroomSolicitationResponse:
    """Aprove a class reservation solicitation"""
    classroom_solicitation_permission_checker(user, solicitation_id, session)
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
    session.refresh(solicitation)
    session.commit()
    EmailService.send_solicitation_approved_email(input, solicitation, background_tasks)
    return ClassroomSolicitationResponse.from_solicitation(solicitation)


@router.put("/deny/{solicitation_id}")
def deny_classroom_solicitation(
    solicitation_id: int,
    input: ClassroomSolicitationDeny,
    session: SessionDep,
    user: UserDep,
    background_tasks: BackgroundTasks,
) -> ClassroomSolicitationResponse:
    """Deny a class reservation solicitation"""
    classroom_solicitation_permission_checker(user, solicitation_id, session)
    solicitation = ClassroomSolicitationRepository.deny(
        id=solicitation_id, user=user, session=session
    )
    session.commit()
    EmailService.send_solicitation_denied_email(input, solicitation, background_tasks)
    return ClassroomSolicitationResponse.from_solicitation(solicitation)


@router.get("/test/assets/uspolis.logo.png")
def get_uspolis_logo() -> FileResponse:
    return FileResponse(image_path)


@router.get("/test/deny/mail", response_class=HTMLResponse)
def test_deny_mail(request: Request, session: SessionDep) -> HTMLResponse:
    solicitation = ClassroomSolicitationRepository.get_by_id(11, session=session)
    input = ClassroomSolicitationDeny(justification="Não quero")
    data = SolicitationDeniedMail.from_solicitation(input, solicitation)
    return templates.TemplateResponse(
        request=request,
        name="solicitation-denied.html",
        context={"data": data.model_dump()},
    )


@router.get("/test/approve/mail", response_class=HTMLResponse)
def test_approve_mail(request: Request, session: SessionDep) -> HTMLResponse:
    solicitation = ClassroomSolicitationRepository.get_by_id(11, session=session)
    input = ClassroomSolicitationApprove(
        classroom_id=10,
        classroom_name="nome",
        start_time=time(19, 0),
        end_time=time(21, 0),
    )
    data = SolicitationApprovedMail.from_solicitation(input, solicitation)
    return templates.TemplateResponse(
        request=request,
        name="solicitation-approved.html",
        context={"data": data.model_dump()},
    )


@router.get("/test/request/mail", response_class=HTMLResponse)
def test_request_mail(
    request: Request, user: UserDep, session: SessionDep
) -> HTMLResponse:
    solicitation = ClassroomSolicitationRepository.get_by_id(11, session=session)
    data = SolicitationRequestedMail.from_solicitation(user, solicitation)
    return templates.TemplateResponse(
        request=request,
        name="solicitation-requested.html",
        context={"data": data.model_dump()},
    )
