import pytest

from server.models.http.requests.calendar_request_models import (
    CalendarInvalidInput,
    CalendarRegister,
    CalendarUpdate,
)


class TestCalendarRegister:
    def test_valid_input_passes(self) -> None:
        calendar = CalendarRegister(name="Calendário 2025", year=2025)

        assert calendar.name == "Calendário 2025"

    def test_rejects_an_empty_name(self) -> None:
        with pytest.raises(CalendarInvalidInput):
            CalendarRegister(name="", year=2025)


class TestCalendarUpdate:
    def test_rejects_an_empty_name(self) -> None:
        with pytest.raises(CalendarInvalidInput):
            CalendarUpdate(name="", year=2025)
