from asyncio import sleep
from fastapi import APIRouter, Body, Response

from server.deps.session_dep import SessionDep
from server.repositories.bug_report_evidence_repository import (
    BugReportEvidenceRepository,
)

embed = Body(..., embed=True)

cookie_router = APIRouter(
    prefix="/reports/evidences",
    tags=["BugReports", "BugReportEvidences"],
)


@cookie_router.get("/{evidence_id}")
def get_report_evidence_cookie(evidence_id: int, session: SessionDep) -> Response:
    evidence = BugReportEvidenceRepository.get_by_id(id=evidence_id, session=session)
    return Response(content=evidence.data, media_type=evidence.mime_type)


router = APIRouter(
    prefix="/reports/evidences",
    tags=["BugReports", "BugReportEvidences"],
)


@router.get("/{evidence_id}")
async def get_report_evidence(evidence_id: int, session: SessionDep) -> Response:
    evidence = BugReportEvidenceRepository.get_by_id(id=evidence_id, session=session)
    await sleep(3)
    return Response(content=evidence.data, media_type=evidence.mime_type)
