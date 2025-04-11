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

    @classmethod
    def from_group(cls, group: Group) -> "GroupResponse":
        return cls(
            id=must_be_int(group.id),
            name=group.name,
            abbreviation=group.abbreviation,
            updated_at=group.updated_at,
            created_at=group.created_at,
        )

    @classmethod
    def from_group_list(cls, groups: list[Group]) -> list["GroupResponse"]:
        return [cls.from_group(group) for group in groups]
