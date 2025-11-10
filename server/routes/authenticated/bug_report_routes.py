import asyncio
from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import JSONResponse

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.bug_report_request_models import BugReportRegister
from server.repositories.bug_report_repository import BugReportRepository
from server.services.email.email_service import EmailService

embed = Body(..., embed=True)

router = APIRouter(prefix="/reports", tags=["BugReports"])


@router.post("")
async def create_bug_report(
    user: UserDep,
    session: SessionDep,
    data: BugReportRegister = Depends(BugReportRegister.as_form),
) -> JSONResponse:
    bug_report = await BugReportRepository.create(data=data, user=user, session=session)
    session.commit()
    asyncio.create_task(EmailService.send_bug_report_email(bug_report))
    return JSONResponse(
        content={"message": "Reporte criado com sucesso!"},
        status_code=status.HTTP_201_CREATED,
    )
