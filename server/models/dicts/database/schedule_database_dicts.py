from server.models.database.allocation_log_db_model import AllocationLog
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.occurrence_db_model import Occurrence
from server.models.database.reservation_db_model import Reservation
from server.models.dicts.base.schedule_base_dict import ScheduleBaseDict
from server.models.dicts.database.base_database_dicts import BaseModelDict
from server.utils.enums.month_week import MonthWeek
from server.utils.enums.week_day import WeekDay


class ScheduleModelDict(ScheduleBaseDict, BaseModelDict, total=False):
    """
    Schedule model dictionary for the database.
    """

    week_day: WeekDay | None
    month_week: MonthWeek | None
    class_id: int | None
    reservation_id: int | None
    classroom_id: int | None

    # Relationships
    class_: Class | None
    reservation: Reservation | None
    classroom: Classroom | None
    occurrences: list[Occurrence]
    logs: list[AllocationLog]
