from datetime import datetime
from pydantic import BaseModel

from server.models.database.allocation_log_db_model import AllocationLog
from server.utils.enums.action_type_enum import ActionType
from server.utils.must_be_int import must_be_int


class AllocationLogResponse(BaseModel):
    id: int
    modified_by: str
    modified_at: datetime
    action: ActionType

    old_classroom: str
    old_building: str
    new_classroom: str
    new_building: str

    schedule_id: int

    @classmethod
    def from_allocation_log(cls, log: AllocationLog) -> "AllocationLogResponse":
        return cls(
            id=must_be_int(log.id),
            modified_by=log.modified_by,
            modified_at=log.modified_at,
            action=log.action,
            old_classroom=log.old_classroom,
            old_building=log.old_building,
            new_classroom=log.new_classroom,
            new_building=log.new_building,
            schedule_id=log.schedule_id,
        )

    @classmethod
    def from_allocation_logs(
        cls, logs: list[AllocationLog]
    ) -> list["AllocationLogResponse"]:
        return [cls.from_allocation_log(log) for log in logs]
