from pydantic import BaseModel


class AllocateSchedule(BaseModel):
    schedule_id: int
    classroom_id: int
    intentional_conflict: bool = False
    intentional_occurrence_ids: list[int] = []
