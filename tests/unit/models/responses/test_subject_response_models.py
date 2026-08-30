from server.models.http.responses.subject_response_models import (
    SubjectResponse,
    SubjectResponseBase,
)
from server.utils.enums.subject_type import SubjectType
from tests.utils.academic_test_utils import make_building, make_subject


class TestSubjectResponseBase:
    def test_core_from_subject(self) -> None:
        subject = make_subject(code="MAC0110", name="Introdução à Computação")

        data = SubjectResponseBase.core_from_subject(subject)

        assert data.id == subject.id
        assert data.code == "MAC0110"
        assert data.name == "Introdução à Computação"
        assert data.professors == subject.professors
        assert data.type == subject.type
        assert data.class_credit == subject.class_credit
        assert data.work_credit == subject.work_credit

    def test_core_from_subject_list(self) -> None:
        subjects = [make_subject(code="MAC0110"), make_subject(code="MAC0323")]

        data = SubjectResponseBase.core_from_subject_list(subjects)

        assert [d.code for d in data] == ["MAC0110", "MAC0323"]


class TestSubjectResponse:
    def test_from_subject_includes_buildings(self) -> None:
        building = make_building(name="Bloco A")
        subject = make_subject(code="MAC0110")
        subject.buildings = [building]

        data = SubjectResponse.from_subject(subject)

        assert data.building_ids == [building.id]
        assert data.buildings[0].name == "Bloco A"

    def test_from_subject_list(self) -> None:
        building = make_building()
        subject1 = make_subject(code="MAC0110")
        subject1.buildings = [building]
        subject2 = make_subject(code="MAC0323")
        subject2.buildings = [building]

        data = SubjectResponse.from_subject_list([subject1, subject2])

        assert [d.code for d in data] == ["MAC0110", "MAC0323"]

    def test_type_is_preserved(self) -> None:
        subject = make_subject()
        subject.type = SubjectType.POSTGRADUATE
        subject.buildings = []

        data = SubjectResponse.from_subject(subject)

        assert data.type == SubjectType.POSTGRADUATE
