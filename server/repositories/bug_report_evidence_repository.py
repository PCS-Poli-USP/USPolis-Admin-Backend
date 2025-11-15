from fastapi import HTTPException, status
from sqlmodel import Session, col, select
from sqlalchemy.exc import NoResultFound
from server.models.database.bug_report_evidence_db_model import (
    BugReportEvidence,
    BugReportEvidenceMetadata,
)
from server.utils.must_be_int import must_be_int


class BugReportEvidenceRepository:
    @staticmethod
    def get_by_id(*, id: int, session: Session) -> BugReportEvidence:
        statement = select(BugReportEvidence).where(col(BugReportEvidence.id) == id)
        try:
            evidence = session.exec(statement).one()
        except NoResultFound:
            raise BugReportEvidenceNotFound(id)
        return evidence

    @staticmethod
    def get_evidences_metadata(
        *, report_id: int, session: Session
    ) -> list[BugReportEvidenceMetadata]:
        statement = select(BugReportEvidence.id, BugReportEvidence.mime_type).where(
            col(BugReportEvidence.report_id) == report_id
        )
        results = session.exec(statement).all()
        return [
            BugReportEvidenceMetadata(
                evidence_id=must_be_int(result[0]),
                report_id=report_id,
                mime_type=result[1],
            )
            for result in results
        ]


class BugReportEvidenceNotFound(HTTPException):
    def __init__(self, id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evidencia de id {id} não existe",
        )
