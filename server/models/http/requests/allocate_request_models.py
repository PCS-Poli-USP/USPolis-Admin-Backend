from pydantic import BaseModel


class AllocateSchedule(BaseModel):
    schedule_id: int
    classroom_id: int
