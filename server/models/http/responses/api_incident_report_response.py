from datetime import datetime

from pydantic import BaseModel

from server.models.database.api_incident_report_db_model import ApiIncidentReport
from server.utils.enums.incident_report_enums import (
    IncidentReportLevel,
    IncidentReportStatus,
)
from server.utils.must_be_int import must_be_int


class ApiIncidentReportResponse(BaseModel):
    id: int
    level: IncidentReportLevel
    status: IncidentReportStatus
    description: str
    access_log_id: int
    access_log_endpoint: str
    access_log_status_code: int
    created_at: datetime
    resolved_at: datetime | None

    @staticmethod
    def from_incident(incident: ApiIncidentReport) -> "ApiIncidentReportResponse":
        return ApiIncidentReportResponse(
            id=must_be_int(incident.id),
            level=incident.level,
            status=incident.status,
            description=incident.description,
            access_log_id=incident.access_log_id,
            access_log_endpoint=incident.access_log.endpoint,
            access_log_status_code=incident.access_log.status_code,
            created_at=incident.created_at,
            resolved_at=incident.resolved_at,
        )

    @staticmethod
    def from_incident_list(
        incidents: list[ApiIncidentReport],
    ) -> list["ApiIncidentReportResponse"]:
        return [ApiIncidentReportResponse.from_incident(i) for i in incidents]
