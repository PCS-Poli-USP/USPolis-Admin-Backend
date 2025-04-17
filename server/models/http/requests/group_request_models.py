from pydantic import BaseModel


class GroupRegister(BaseModel):
    name: str
    classroom_ids: list[int] = []
    user_ids: list[int] = []


class GroupUpdate(GroupRegister):
    pass
