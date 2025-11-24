from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship
from server.models.database.base_db_model import BaseModel

if TYPE_CHECKING:
    from server.models.database.bug_report_db_model import BugReport


class BugReportEvidence(BaseModel, table=True):
    report_id: int = Field(foreign_key="bugreport.id", nullable=False)
    data: bytes
    mime_type: str

    report: "BugReport" = Relationship(back_populates="evidences")


class BugReportEvidenceMetadata(BaseModel):
    evidence_id: int
    report_id: int
    mime_type: str
