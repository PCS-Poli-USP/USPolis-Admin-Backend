"""Shared, DB-free helpers for building Schedule/Class/Calendar/Holiday
object graphs in pure unit tests (no session, nothing persisted) - keep
every such helper here instead of redeclaring local make_* functions per
test file."""

from datetime import date, time

from server.models.database.calendar_db_model import Calendar
from server.models.database.class_db_model import Class
from server.models.database.holiday_category_db_model import HolidayCategory
from server.models.database.holiday_db_model import Holiday
from server.models.database.schedule_db_model import Schedule
from server.utils.enums.audiovisual_type_enum import AudiovisualType
from server.utils.enums.class_type import ClassType
from server.utils.enums.month_week import MonthWeek
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.week_day import WeekDay


def make_schedule(
    *,
    recurrence: Recurrence,
    start_date: date,
    end_date: date,
    week_day: WeekDay | None = None,
    month_week: MonthWeek | None = None,
    start_time: time = time(8, 0),
    end_time: time = time(10, 0),
) -> Schedule:
    return Schedule(
        id=1,
        start_date=start_date,
        end_date=end_date,
        start_time=start_time,
        end_time=end_time,
        week_day=week_day,
        recurrence=recurrence,
        month_week=month_week,
    )


def make_class_with_holidays(*, holiday_dates: list[date]) -> Class:
    category = HolidayCategory(id=1, name="Feriados", year=2025, created_by_id=1)
    category.holidays = [
        Holiday(id=idx, name="Feriado", date=d, category_id=1, created_by_id=1)
        for idx, d in enumerate(holiday_dates, start=1)
    ]
    calendar = Calendar(id=1, name="Calendario", year=2025, created_by_id=1)
    calendar.categories = [category]
    class_ = Class(
        id=1,
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
        code="MAC0110",
        professors=[],
        type=ClassType.THEORIC,
        vacancies=1,
        audiovisual=AudiovisualType.NONE,
        subject_id=1,
    )
    class_.calendars = [calendar]
    return class_
