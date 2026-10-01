from datetime import date, time

import pytest
from pydantic import ValidationError

from server.models.http.requests.occurrence_request_models import (
    OccurenceManyRegister,
)


class TestOccurenceManyRegister:
    def test_valid_input_passes(self) -> None:
        register = OccurenceManyRegister(
            start_time=time(8, 0),
            end_time=time(10, 0),
            dates=[date(2025, 1, 6), date(2025, 1, 13)],
            labels=["Aula 1", "Aula 2"],
            times=[(time(8, 0), time(10, 0)), (time(9, 0), time(11, 0))],
        )

        assert len(register.dates) == 2

    def test_rejects_mismatched_labels_length(self) -> None:
        with pytest.raises(ValidationError, match="labels must match"):
            OccurenceManyRegister(
                start_time=time(8, 0),
                end_time=time(10, 0),
                dates=[date(2025, 1, 6), date(2025, 1, 13)],
                labels=["Aula 1"],
            )

    def test_rejects_mismatched_times_length(self) -> None:
        with pytest.raises(ValidationError, match="times must match"):
            OccurenceManyRegister(
                start_time=time(8, 0),
                end_time=time(10, 0),
                dates=[date(2025, 1, 6), date(2025, 1, 13)],
                times=[(time(8, 0), time(10, 0))],
            )
