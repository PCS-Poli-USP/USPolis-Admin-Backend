from pydantic import BaseModel

from server.models.database.classroom_db_model import ConflictsInfo


class AllocateSchedule(BaseModel):
    schedule_id: int
    classroom_id: int
    intentional_conflict: bool = False
    conflict_infos: list[ConflictsInfo] = []
