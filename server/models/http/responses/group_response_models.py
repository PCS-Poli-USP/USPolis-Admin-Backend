from datetime import datetime
from pydantic import BaseModel

from server.models.database.group_db_model import Group
from server.utils.must_be_int import must_be_int


class GroupResponse(BaseModel):
    id: int
    name: str
    abbreviation: str
    updated_at: datetime
    created_at: datetime

    user_ids: list[int]
    user_strs: list[str]
    classroom_ids: list[int]
    classroom_strs: list[str]

    @classmethod
    def from_group(cls, group: Group) -> "GroupResponse":
        return cls(
            id=must_be_int(group.id),
            name=group.name,
            abbreviation=group.abbreviation,
            updated_at=group.updated_at,
            created_at=group.created_at,
            user_ids=[must_be_int(user.id) for user in group.users],  # noqa: F811
            user_strs=[f"{user.name} ({user.email})" for user in group.users],  # noqa: F811
            classroom_ids=[must_be_int(classroom.id) for classroom in group.classrooms],
            classroom_strs=[
                f"{classroom.name} ({classroom.building.name})"
                for classroom in group.classrooms
            ],
        )

    @classmethod
    def from_group_list(cls, groups: list[Group]) -> list["GroupResponse"]:
        return [cls.from_group(group) for group in groups]
