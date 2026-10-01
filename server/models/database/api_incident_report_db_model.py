from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, Text
from sqlmodel import Field, Relationship, Enum

from server.models.database.base_db_model import BaseModel
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.incident_report_enums import (
    IncidentReportLevel,
    IncidentReportStatus,
)

if TYPE_CHECKING:
    from server.models.database.api_access_log_db_model import ApiAccessLog


class ApiIncidentReport(BaseModel, table=True):
    level: IncidentReportLevel = Field(
        sa_column=Column(Enum(IncidentReportLevel), nullable=False)
    )
    status: IncidentReportStatus = Field(
        sa_column=Column(Enum(IncidentReportStatus), nullable=False, index=True),
        default=IncidentReportStatus.OPEN,
    )
    description: str = Field(sa_column=Column(Text, nullable=False))
    access_log_id: int = Field(foreign_key="apiaccesslog.id", nullable=False)
    created_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    resolved_at: datetime | None = Field(default=None, nullable=True)

    access_log: "ApiAccessLog" = Relationship()
