from pydantic import BaseModel


class UserScheduleRegister(BaseModel):
    schedule_ids: list[int]


class UserScheduleUpdate(UserScheduleRegister):
    pass
