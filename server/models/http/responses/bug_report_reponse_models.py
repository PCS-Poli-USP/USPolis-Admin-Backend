from datetime import datetime
from pydantic import BaseModel
from sqlmodel import Session

from server.models.database.bug_report_db_model import BugReport
from server.repositories.bug_report_evidence_repository import (
    BugReportEvidenceRepository,
)
from server.utils.enums.bug_enums import BugPriority, BugStatus, BugType
from server.utils.must_be_int import must_be_int


class BugReportResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    user_email: str

    priority: BugPriority
    type: BugType
    status: BugStatus
    description: str
    created_at: datetime
    resolved_at: datetime | None

    evidences_ids: list[int]
    mime_types: list[str]

    @staticmethod
    def from_report(bug_report: BugReport, session: Session) -> "BugReportResponse":
        report_id = must_be_int(bug_report.id)
        evidence_metas = BugReportEvidenceRepository.get_evidences_metadata(
            report_id=report_id, session=session
        )
        return BugReportResponse(
            id=report_id,
            user_id=bug_report.user_id,
            user_name=bug_report.user.name,
            user_email=bug_report.user.email,
            priority=bug_report.priority,
            type=bug_report.type,
            status=bug_report.status,
            description=bug_report.description,
            created_at=bug_report.created_at,
            resolved_at=bug_report.resolved_at,
            evidences_ids=[meta.evidence_id for meta in evidence_metas],
            mime_types=[meta.mime_type for meta in evidence_metas],
        )

    @staticmethod
    def from_reports(
        reports: list[BugReport], session: Session
    ) -> list["BugReportResponse"]:
        return [BugReportResponse.from_report(report, session) for report in reports]
