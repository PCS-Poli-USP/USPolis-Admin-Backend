import pytest

from server.models.http.requests.api_incident_report_request_models import (
    ApiIncidentReportCreateRequest,
    ApiIncidentReportInvalidInput,
)
from server.utils.enums.incident_report_enums import IncidentReportLevel


class TestApiIncidentReportCreateRequest:
    def test_valid_input_passes(self) -> None:
        request = ApiIncidentReportCreateRequest(
            access_log_id=1,
            level=IncidentReportLevel.HIGH,
            description="Erro 500 recorrente",
        )

        assert request.description == "Erro 500 recorrente"

    def test_rejects_an_empty_description(self) -> None:
        with pytest.raises(ApiIncidentReportInvalidInput):
            ApiIncidentReportCreateRequest(
                access_log_id=1, level=IncidentReportLevel.HIGH, description=""
            )
