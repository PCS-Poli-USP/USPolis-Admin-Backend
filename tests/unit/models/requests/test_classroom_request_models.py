from server.models.http.requests.classroom_request_models import (
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

    def test_groups_are_optional(self) -> None:
        assert ClassroomRegister(**_base_kwargs()).group_ids == []
        assert ClassroomRegister(group_ids=[], **_base_kwargs()).group_ids == []


class TestClassroomUpdate:
    def test_groups_are_optional(self) -> None:
        assert ClassroomUpdate(group_ids=[], **_base_kwargs()).group_ids == []
