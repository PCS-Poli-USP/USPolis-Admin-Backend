from datetime import time

from server.models.http.responses.occupance_reports_response import (
    OccupanceReportsResponse,
)
from server.services.occupance_reports_service import OccuppanceReportDict
from server.utils.enums.week_day import WeekDay


def _make_report_dict(**overrides: object) -> OccuppanceReportDict:
    default: OccuppanceReportDict = {
        "week_day": WeekDay.MONDAY,
        "classroom": "Sala 1",
        "capacity": 40,
        "classes": ["MAC0110"],
        "start_time": time(8, 0),
        "end_time": time(10, 0),
        "students": 30,
        "percentage": 0.75,
        "class_id": [1],
    }
    default.update(overrides)  # type: ignore[typeddict-item]
    return default


class TestOccupanceReportsResponse:
    def test_from_dict(self) -> None:
        value = _make_report_dict(classroom="Sala 2", students=20)

        data = OccupanceReportsResponse.from_dict(value)

        assert data.classroom == "Sala 2"
        assert data.students == 20
        assert data.week_day == WeekDay.MONDAY

    def test_from_dicts(self) -> None:
        value1 = _make_report_dict(classroom="Sala 1")
        value2 = _make_report_dict(classroom="Sala 2")

        data = OccupanceReportsResponse.from_dicts([value1, value2])

        assert [d.classroom for d in data] == ["Sala 1", "Sala 2"]
