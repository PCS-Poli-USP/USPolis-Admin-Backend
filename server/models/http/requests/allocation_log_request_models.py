from datetime import datetime
from pydantic import BaseModel

from server.models.database.classroom_db_model import Classroom
from server.models.database.schedule_db_model import Schedule
from server.models.database.user_db_model import User
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.action_type_enum import ActionType
from server.utils.enums.allocation_enum import AllocationEnum
from server.utils.must_be_int import must_be_int


class AllocationLogBase(BaseModel):
    modified_by: str
    modified_at: datetime
    action: ActionType

    old_classroom: str
    old_building: str

    new_classroom: str
    new_building: str


class AllocationLogInput(AllocationLogBase):
    schedule_id: int | None
    schedule: Schedule

    @classmethod
    def for_deallocation(cls, user: User, schedule: Schedule) -> "AllocationLogInput":
        return cls(
            schedule_id=must_be_int(schedule.id),
            schedule=schedule,
            modified_by=user.name,
            modified_at=BrazilDatetime.now_utc(),
            action=ActionType.ALLOCATE,
            old_classroom=str(schedule.classroom.name)
            if schedule.classroom
            else AllocationEnum.UNALLOCATED.value,
            old_building=str(schedule.classroom.building.name)
            if schedule.classroom
            else AllocationEnum.UNALLOCATED.value,
            new_classroom=AllocationEnum.UNALLOCATED.value,
            new_building=AllocationEnum.UNALLOCATED.value,
        )

    @classmethod
    def for_allocation(
        cls, user: User, schedule: Schedule, classroom: Classroom
    ) -> "AllocationLogInput":
        return cls(
            schedule_id=schedule.id,
            schedule=schedule,
            modified_by=user.name,
            modified_at=BrazilDatetime.now_utc(),
            action=ActionType.ALLOCATE,
            old_classroom=str(schedule.classroom.name)
            if schedule.classroom
            else AllocationEnum.UNALLOCATED.value,
            old_building=str(schedule.classroom.building.name)
            if schedule.classroom
            else AllocationEnum.UNALLOCATED.value,
            new_classroom=classroom.name,
            new_building=classroom.building.name,
        )
