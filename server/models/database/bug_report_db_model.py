from datetime import datetime
from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship, Column, Enum, Text
from server.models.database.base_db_model import BaseModel
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.bug_enums import BugPriority, BugStatus, BugType

if TYPE_CHECKING:
    from server.models.database.user_db_model import User
    from server.models.database.bug_report_evidence_db_model import BugReportEvidence


class BugReport(BaseModel, table=True):
    user_id: int = Field(foreign_key="user.id", nullable=False)
    priority: BugPriority = Field(sa_column=Column(Enum(BugPriority), nullable=False))
    type: BugType = Field(sa_column=Column(Enum(BugType), nullable=False))
    status: BugStatus = Field(sa_column=Column(Enum(BugStatus), nullable=False))
    description: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(default_factory=BrazilDatetime.now)
    resolved_at: datetime | None = Field(default_factory=lambda: None)

    user: "User" = Relationship(back_populates="reports")
    evidences: "BugReportEvidence" = Relationship(back_populates="report")
