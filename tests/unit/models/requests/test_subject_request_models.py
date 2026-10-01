import pytest

from server.models.http.requests.subject_request_models import (
    SubjectInvalidData,
    SubjectRegister,
)
from server.utils.enums.subject_type import SubjectType


def _base_kwargs() -> dict:
    return {
        "name": "Introdução à Computação",
        "professors": [],
        "type": SubjectType.BIANNUAL,
        "class_credit": 4,
        "work_credit": 0,
    }


class TestSubjectRegister:
    def test_valid_input_passes(self) -> None:
        subject = SubjectRegister(building_ids=[1], code="MAC0110", **_base_kwargs())

        assert subject.code == "MAC0110"

    def test_rejects_a_code_with_the_wrong_length(self) -> None:
        with pytest.raises(SubjectInvalidData):
            SubjectRegister(building_ids=[1], code="MAC1", **_base_kwargs())

    def test_rejects_empty_building_ids(self) -> None:
        with pytest.raises(SubjectInvalidData):
            SubjectRegister(building_ids=[], code="MAC0110", **_base_kwargs())
