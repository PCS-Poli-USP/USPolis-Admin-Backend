from fastapi import APIRouter, Body, status
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.solicitation_request_models import (
    SolicitationApprove,
    SolicitationDeny,
)
from server.repositories.solicitation_repository import (
    SolicitationRepository,
)
from server.services.email.email_service import EmailService
from server.services.security.solicitation_permission_checker import (
    SolicitationPermissionChecker,
)
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


@router.put("/approve/{solicitation_id}")
async def approve_reservation_solicitation(
    solicitation_id: int,
    input: SolicitationApprove,
    session: SessionDep,
    user: UserDep,
) -> JSONResponse:
    """Aprove a class reservation solicitation"""
    checker = SolicitationPermissionChecker(user, session)
    checker.check_permission(solicitation_id)
    solicitation = SolicitationRepository.approve(
        id=solicitation_id, classroom_id=input.classroom_id, user=user, session=session
    )
    session.refresh(solicitation)
    session.commit()
    await EmailService.send_solicitation_approved_email(input, solicitation)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Solicitação aprovada com sucesso."},
    )


@router.put("/deny/{solicitation_id}")
async def deny_classroom_solicitation(
    solicitation_id: int,
    input: SolicitationDeny,
    session: SessionDep,
    user: UserDep,
) -> JSONResponse:
    """Deny a class reservation solicitation"""
    checker = SolicitationPermissionChecker(user, session)
    checker.check_permission(solicitation_id)

    solicitation = SolicitationRepository.deny(
        id=solicitation_id, user=user, session=session
    )
    session.commit()
    await EmailService.send_solicitation_denied_email(input, solicitation)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Solicitação negada com sucesso."},
    )
