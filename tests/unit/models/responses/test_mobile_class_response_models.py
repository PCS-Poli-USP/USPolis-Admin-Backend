from datetime import date

import pytest

from server.deps.interval_dep import QueryInterval
from server.models.http.exceptions.responses_exceptions import UnfetchDataError
from server.models.http.responses.mobile_class_response_models import (
    MobileClassResponse,
)
from tests.utils.academic_test_utils import make_class, make_subject
from tests.utils.time_test_utils import make_schedule


class TestMobileClassResponseFromModel:
    def test_builds_from_a_class_with_its_schedules(self) -> None:
        subject = make_subject(code="MAC0110", name="Introdução à Computação")
        class_ = make_class(subject=subject, code="T01")
        schedule = make_schedule(class_=class_)
        class_.schedules = [schedule]

        data = MobileClassResponse.from_model(class_)

        assert data.id == class_.id
        assert data.code == "T01"
        assert data.subject_name == "Introdução à Computação"
        assert data.subject_code == "MAC0110"
        assert data.subject_id == subject.id
        assert [s.id for s in data.schedules] == [schedule.id]

    def test_raises_when_class_has_no_id(self) -> None:
        subject = make_subject()
        class_ = make_class(subject=subject)
        class_.id = None

        with pytest.raises(UnfetchDataError):
            MobileClassResponse.from_model(class_)

    def test_raises_when_subject_has_no_id(self) -> None:
        subject = make_subject()
        class_ = make_class(subject=subject)
        subject.id = None

        with pytest.raises(UnfetchDataError):
            MobileClassResponse.from_model(class_)

    def test_filters_schedules_ending_before_today(self) -> None:
        subject = make_subject()
        class_ = make_class(subject=subject)
        ending_soon = make_schedule(
            class_=class_,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
        )
        ending_later = make_schedule(
            class_=class_,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )
        class_.schedules = [ending_soon, ending_later]
        interval = QueryInterval(today=date(2025, 6, 1))

        data = MobileClassResponse.from_model(class_, interval)

        assert [s.id for s in data.schedules] == [ending_later.id]

    def test_filters_schedules_outside_a_start_end_range(self) -> None:
        subject = make_subject()
        class_ = make_class(subject=subject)
        inside_range = make_schedule(
            class_=class_,
            start_date=date(2025, 3, 1),
            end_date=date(2025, 3, 31),
        )
        outside_range = make_schedule(
            class_=class_,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
        )
        class_.schedules = [inside_range, outside_range]
        interval = QueryInterval(start=date(2025, 2, 1), end=date(2025, 4, 1))

        data = MobileClassResponse.from_model(class_, interval)

        assert [s.id for s in data.schedules] == [inside_range.id]

    def test_from_model_list(self) -> None:
        subject = make_subject()
        class1 = make_class(subject=subject)
        class1.schedules = []
        class2 = make_class(subject=subject)
        class2.schedules = []

        data = MobileClassResponse.from_model_list([class1, class2])

        assert [d.id for d in data] == [class1.id, class2.id]
