from pydantic import BaseModel


class GroupRegister(BaseModel):
    building_id: int
    name: str
    classroom_ids: list[int] | None
    user_ids: list[int] = []


class GroupUpdate(GroupRegister):
    pass
