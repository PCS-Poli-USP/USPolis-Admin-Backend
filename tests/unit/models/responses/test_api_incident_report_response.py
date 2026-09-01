from datetime import datetime

from server.models.database.api_incident_report_db_model import ApiIncidentReport
from server.models.http.responses.api_incident_report_response import (
    ApiIncidentReportResponse,
)
from server.utils.enums.incident_report_enums import (
    IncidentReportLevel,
    IncidentReportStatus,
)
from tests.utils.api_log_test_utils import make_api_access_log

_next_id = iter(range(1, 1_000_000))


def _make_incident(
    *, access_log: ApiIncidentReport | None = None
) -> ApiIncidentReport:
    log = make_api_access_log(endpoint="/api/classrooms", status_code=500)
    incident = ApiIncidentReport(
        id=next(_next_id),
        level=IncidentReportLevel.HIGH,
        status=IncidentReportStatus.OPEN,
        description="Erro 500 recorrente",
        access_log_id=log.id,
        created_at=datetime(2025, 1, 1),
        resolved_at=None,
    )
    incident.access_log = log
    return incident


class TestApiIncidentReportResponse:
    def test_from_incident(self) -> None:
        incident = _make_incident()

        data = ApiIncidentReportResponse.from_incident(incident)

        assert data.id == incident.id
        assert data.level == IncidentReportLevel.HIGH
        assert data.status == IncidentReportStatus.OPEN
        assert data.description == "Erro 500 recorrente"
        assert data.access_log_endpoint == "/api/classrooms"
        assert data.access_log_status_code == 500

    def test_from_incident_list(self) -> None:
        incident1 = _make_incident()
        incident2 = _make_incident()

        data = ApiIncidentReportResponse.from_incident_list([incident1, incident2])

        assert [d.id for d in data] == [incident1.id, incident2.id]
