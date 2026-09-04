from datetime import datetime

import pytest
from pydantic import ValidationError

from server.models.http.requests.holiday_request_models import (
    HolidayManyRegister,
    HolidayRegister,
    HolidayUpdate,
)


class TestHolidayRegister:
    def test_valid_input_passes(self) -> None:
        holiday = HolidayRegister(
            category_id=1, name="Independência", date=datetime(2025, 9, 7)
        )

        assert holiday.name == "Independência"

    def test_rejects_an_empty_name(self) -> None:
        with pytest.raises(ValidationError):
            HolidayRegister(category_id=1, name="", date=datetime(2025, 9, 7))


class TestHolidayUpdate:
    def test_rejects_an_empty_name(self) -> None:
        with pytest.raises(ValidationError):
            HolidayUpdate(category_id=1, name="", date=datetime(2025, 9, 7))


class TestHolidayManyRegister:
    def test_rejects_an_empty_name(self) -> None:
        with pytest.raises(ValidationError):
            HolidayManyRegister(
                category_id=1, name="", dates=[datetime(2025, 9, 7)]
            )
