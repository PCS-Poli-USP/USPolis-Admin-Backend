from datetime import datetime
from pydantic import BaseModel

from server.models.database.group_db_model import Group
from server.utils.must_be_int import must_be_int


class GroupResponse(BaseModel):
    id: int
    building_id: int
    building: str
    name: str
    updated_at: datetime
    created_at: datetime
    main: bool

    user_ids: list[int]
    user_strs: list[str]
    classroom_ids: list[int]
    classroom_strs: list[str]

    @classmethod
    def from_group(cls, group: Group) -> "GroupResponse":
        classrooms = group.classrooms
        if group.main:
            classrooms = group.building.classrooms if group.building.classrooms else []
            classrooms.sort(key=lambda c: c.name)

        return cls(
            id=must_be_int(group.id),
            building_id=must_be_int(group.building_id),
            building=group.building.name,
            name=group.name,
            main=group.main,
            updated_at=group.updated_at,
            created_at=group.created_at,
            user_ids=[must_be_int(user.id) for user in group.users],  # noqa: F811
            user_strs=[f"{user.name} ({user.email})" for user in group.users],  # noqa: F811
            classroom_ids=[must_be_int(classroom.id) for classroom in classrooms],
            classroom_strs=[
                f"{classroom.name} ({classroom.building.name})"
                for classroom in classrooms
            ],
        )

    @classmethod
    def from_group_list(cls, groups: list[Group]) -> list["GroupResponse"]:
        return [cls.from_group(group) for group in groups]
