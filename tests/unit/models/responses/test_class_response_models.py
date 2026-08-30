from sqlmodel import Session

from server.models.http.responses.class_response_models import (
    ClassCoreResponse,
    ClassFullResponse,
    ClassResponse,
    ClassResponseBase,
    ClassSchedulingResponse,
)
from tests.factories.model.calendar_model_factory import CalendarModelFactory
from tests.utils.academic_test_utils import (
    make_building,
    make_class,
    make_subject,
    make_user,
)


class TestClassCoreResponse:
    def test_from_class(self) -> None:
        subject = make_subject(code="MAC0110", name="Introdução à Computação")
        class_ = make_class(subject=subject, code="T01", vacancies=35)

        data = ClassCoreResponse.from_class(class_)

        assert data.id == class_.id
        assert data.code == "T01"
        assert data.vacancies == 35
        assert data.subject_id == subject.id
        assert data.subject_code == "MAC0110"
        assert data.subject_name == "Introdução à Computação"


class TestClassResponseBase:
    def test_from_class_without_calendars(self) -> None:
        subject = make_subject(code="MAC0110")
        class_ = make_class(subject=subject)

        data = ClassResponseBase.from_class(class_)

        assert data.calendar_ids == []
        assert data.calendar_names == []

    def test_from_class_with_subject_buildings(self) -> None:
        building = make_building(name="Bloco A")
        subject = make_subject(code="MAC0110")
        subject.buildings = [building]
        class_ = make_class(subject=subject)

        data = ClassResponseBase.from_class(class_)

        assert data.subject_building_ids == [building.id]


class TestClassSchedulingResponse:
    def test_from_class_includes_schedules(self) -> None:
        subject = make_subject()
        class_ = make_class(subject=subject)
        class_.schedules = []

        data = ClassSchedulingResponse.from_class(class_)

        assert data.schedules == []

    def test_from_class_list(self) -> None:
        subject = make_subject()
        class1 = make_class(subject=subject)
        class1.schedules = []
        class2 = make_class(subject=subject)
        class2.schedules = []

        data = ClassSchedulingResponse.from_class_list([class1, class2])

        assert [d.id for d in data] == [class1.id, class2.id]


class TestClassResponse:
    def test_from_class(self) -> None:
        subject = make_subject()
        class_ = make_class(subject=subject)
        class_.schedules = []

        data = ClassResponse.from_class(class_)

        assert data.id == class_.id
        assert data.schedules == []

    def test_from_class_list(self) -> None:
        subject = make_subject()
        class1 = make_class(subject=subject)
        class1.schedules = []
        class2 = make_class(subject=subject)
        class2.schedules = []

        data = ClassResponse.from_class_list([class1, class2])

        assert [d.id for d in data] == [class1.id, class2.id]


class TestClassFullResponse:
    def test_from_class(self) -> None:
        subject = make_subject()
        class_ = make_class(subject=subject)
        class_.schedules = []

        data = ClassFullResponse.from_class(class_)

        assert data.id == class_.id
        assert data.schedules == []

    def test_from_class_list(self) -> None:
        subject = make_subject()
        class1 = make_class(subject=subject)
        class1.schedules = []
        class2 = make_class(subject=subject)
        class2.schedules = []

        data = ClassFullResponse.from_class_list([class1, class2])

        assert [d.id for d in data] == [class1.id, class2.id]


class TestClassResponseWithCalendars:
    def test_from_class_includes_calendar_ids_and_names(self) -> None:
        subject = make_subject()
        class_ = make_class(subject=subject)
        creator = make_user()
        calendar = CalendarModelFactory(creator=creator, session=Session()).build(
            name="Calendario 2025"
        )
        calendar.id = 1
        class_.calendars = [calendar]

        data = ClassResponseBase.from_class(class_)

        assert data.calendar_ids == [1]
        assert data.calendar_names == ["Calendario 2025"]
