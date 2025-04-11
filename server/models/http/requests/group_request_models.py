from datetime import datetime
from pydantic import BaseModel, Field


class GroupRegister(BaseModel):
    name: str
    abbreviation: str = Field(max_length=10)
    updated_at: datetime = Field(default=datetime.now())
    created_at: datetime = Field(default=datetime.now())

    classroom_ids: list[int] = []


class GroupUpdate(GroupRegister):
    pass
