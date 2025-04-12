from pydantic import BaseModel, Field


class GroupRegister(BaseModel):
    name: str
    abbreviation: str = Field(max_length=10)
    classroom_ids: list[int] = []
    user_ids: list[int] = []


class GroupUpdate(GroupRegister):
    pass
