from fastapi import APIRouter, Body, status
from fastapi.responses import JSONResponse

from server.deps.session_dep import SessionDep
from server.models.http.requests.bug_report_request_models import BugReportStatusUpdate
from server.models.http.responses.bug_report_reponse_models import BugReportResponse
from server.repositories.bug_report_repository import BugReportRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/reports", tags=["BugReports"])


@router.get("")
def get_all_reports(session: SessionDep) -> list[BugReportResponse]:
    reports = BugReportRepository.get_all(session=session)
    return BugReportResponse.from_reports(reports, session)


@router.patch("/{report_id}")
def update_report_status(
    report_id: int, data: BugReportStatusUpdate, session: SessionDep
) -> JSONResponse:
    BugReportRepository.update_status(id=report_id, status=data.status, session=session)
    session.commit()
    return JSONResponse(
        content={"message": "Relatório atualizado com sucesso!"},
        status_code=status.HTTP_200_OK,
    )
