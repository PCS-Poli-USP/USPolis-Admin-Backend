import asyncio
from fastapi import APIRouter, Body, status
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from server.deps.repository_adapters.solicitation_repository_adapter import (
    SolicitationRepositoryDep,
)
from server.models.http.requests.solicitation_request_models import (
    SolicitationApprove,
    SolicitationDeny,
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


@router.put("/approve/{solicitation_id}")
async def approve_reservation_solicitation(
    solicitation_id: int,
    input: SolicitationApprove,
    solicitation_repo: SolicitationRepositoryDep,
) -> JSONResponse:
    """Aprove a class reservation solicitation"""
    solicitation = solicitation_repo.approve(solicitation_id, input)
    asyncio.create_task(
        EmailService.send_solicitation_approved_email(input, solicitation)
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Solicitação aprovada com sucesso."},
    )


@router.put("/deny/{solicitation_id}")
async def deny_classroom_solicitation(
    solicitation_id: int,
    input: SolicitationDeny,
    solicitation_repo: SolicitationRepositoryDep,
) -> JSONResponse:
    """Deny a class reservation solicitation"""
    solicitation = solicitation_repo.deny(solicitation_id, input)
    asyncio.create_task(
        EmailService.send_solicitation_denied_email(input, solicitation)
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Solicitação negada com sucesso."},
    )
