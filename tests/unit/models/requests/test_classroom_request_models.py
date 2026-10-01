import pytest

from server.models.http.requests.classroom_request_models import (
    ClassroomInvalidRequest,
    ClassroomRegister,
    ClassroomUpdate,
)
from server.utils.enums.audiovisual_type_enum import AudiovisualType


def _base_kwargs() -> dict:
    return {
        "building_id": 1,
        "name": "Sala 1",
        "capacity": 40,
        "floor": 2,
        "accessibility": True,
        "audiovisual": AudiovisualType.NONE,
        "air_conditioning": False,
    }


class TestClassroomRegister:
    def test_valid_input_passes(self) -> None:
        classroom = ClassroomRegister(group_ids=[1], **_base_kwargs())

        assert classroom.group_ids == [1]

    def test_rejects_no_groups(self) -> None:
        with pytest.raises(ClassroomInvalidRequest):
            ClassroomRegister(group_ids=[], **_base_kwargs())


class TestClassroomUpdate:
    def test_rejects_no_groups(self) -> None:
        with pytest.raises(ClassroomInvalidRequest):
            ClassroomUpdate(group_ids=[], **_base_kwargs())
