from fastapi import HTTPException, status
from sqlmodel import Session, col, select
from sqlalchemy.exc import NoResultFound
from server.models.database.bug_report_db_model import BugReport
from server.models.database.bug_report_evidence_db_model import BugReportEvidence
from server.models.database.user_db_model import User
from server.models.http.requests.bug_report_request_models import BugReportRegister
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.bug_enums import BugStatus
from server.utils.must_be_int import must_be_int


class BugReportRepository:
    @staticmethod
    def get_all(*, session: Session) -> list[BugReport]:
        statement = select(BugReport)
        return list(session.exec(statement).all())

    @staticmethod
    def get_by_id(*, id: int, session: Session) -> BugReport:
        statement = select(BugReport).where(col(BugReport.id) == id)
        try:
            report = session.exec(statement).one()
        except NoResultFound:
            raise BugReportNotFound(id)
        return report

    @staticmethod
    async def create(
        *, data: BugReportRegister, user: User, session: Session
    ) -> BugReport:
        bug_report = BugReport(
            user_id=must_be_int(user.id),
            user=user,
            priority=data.priority,
            type=data.type,
            status=data.status,
            description=data.description,
        )
        session.add(bug_report)
        session.flush()

        for img in data.evidences:
            content = await img.read()
            evidence = BugReportEvidence(
                report_id=must_be_int(bug_report.id),
                report=bug_report,
                mime_type=img.content_type or "",
                data=content,
            )
            session.add(evidence)

        return bug_report

    @staticmethod
    def update_status(*, id: int, status: BugStatus, session: Session) -> BugReport:
        """Update the BugReportStatus, if the new status is RESOLVED also update column 'resolved_at'\n"""
        report = BugReportRepository.get_by_id(id=id, session=session)
        report.status = status
        if status == BugStatus.RESOLVED:
            report.resolved_at = BrazilDatetime.now_utc()
        if status != BugStatus.RESOLVED:
            report.resolved_at = None
        session.add(report)
        return report


class BugReportNotFound(HTTPException):
    def __init__(self, id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"O relatório de id {id} não existe",
        )
