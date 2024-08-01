from datetime import date, timedelta

from server.models.database.occurrence_db_model import Occurrence
from server.models.database.schedule_db_model import Schedule
from server.utils.enums.month_week import MonthWeek
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.week_day import WeekDay


class OccurrenceUtils:
    # TODO: dont create occurrences on holidays
    # update/delete schedules
    @staticmethod
    def generate_occurrences(schedule: Schedule) -> list[Occurrence]:
        occurrences: list[Occurrence] = []
        if schedule.week_day is None and schedule.recurrence is not Recurrence.DAILY:
            raise ValueError("Week day is required with this Recurrence")
        if schedule.recurrence is Recurrence.CUSTOM:
            raise ValueError("Recurrence Custom is not valid with this method")
        dates = OccurrenceUtils._dates_for_recurrence(
            schedule.week_day.value if schedule.week_day else -1,
            schedule.recurrence,
            schedule.start_date,
            schedule.end_date,
            schedule.month_week.value if schedule.month_week else None,
        )
        calendars = []
        if schedule.class_:
            calendars = schedule.class_.calendars
        for occ_date in dates:
            if any(
                calendar.dates()
                for calendar in calendars
                if occ_date in calendar.dates()
            ):
                continue
            occurrence = Occurrence(
                date=occ_date,
                start_time=schedule.start_time,
                end_time=schedule.end_time,
                schedule_id=schedule.id,
            )
            occurrences.append(occurrence)
        return occurrences

    @staticmethod
    def get_weekday_date_for_month_week(
        year: int, month: int, week_day: int, month_week: int
    ) -> date:
        first_date = date(year, month, 1)
        days_to_first_week_day = (week_day - first_date.weekday() + 7) % 7
        first_week_day_date = first_date + timedelta(days=days_to_first_week_day)
        if month_week == MonthWeek.LAST.value:
            last_week_day_date = first_week_day_date + timedelta(weeks=4)
            if last_week_day_date.month > month or (
                last_week_day_date.month == 1 and month == 12
            ):
                last_week_day_date -= timedelta(weeks=1)
            return last_week_day_date
        else:
            return first_week_day_date + timedelta(weeks=(month_week - 1))

    @staticmethod
    def _dates_for_recurrence(
        week_day: int,
        recurrence: Recurrence,
        start_date: date,
        end_date: date,
        month_week: int | None = None,
    ) -> list[date]:
        dates: list[date] = []
        match recurrence:
            case Recurrence.WEEKLY:
                days_to_first_weekday = (week_day - start_date.weekday() + 7) % 7
                first_weekday_date = start_date + timedelta(days=days_to_first_weekday)
                current_date = first_weekday_date
                while current_date <= end_date:
                    dates.append(current_date)
                    current_date += timedelta(days=7)

            case Recurrence.BIWEEKLY:
                days_to_first_weekday = (week_day - start_date.weekday() + 7) % 7
                first_weekday_date = start_date + timedelta(days=days_to_first_weekday)
                current_date = first_weekday_date
                while current_date <= end_date:
                    dates.append(current_date)
                    current_date += timedelta(days=14)

            case Recurrence.MONTHLY:
                if month_week is None:
                    raise ValueError("Month week is required for monthly recurrence")
                current_date = start_date
                while current_date <= end_date:
                    week_day_date = OccurrenceUtils.get_weekday_date_for_month_week(
                        current_date.year, current_date.month, week_day, month_week
                    )
                    if start_date <= week_day_date <= end_date:
                        dates.append(week_day_date)
                    if current_date.month == 12:
                        current_date = date(current_date.year + 1, 1, 1)
                    else:
                        current_date = date(
                            current_date.year, current_date.month + 1, 1
                        )

            case Recurrence.DAILY:
                current_date = start_date
                while current_date <= end_date:
                    if current_date.weekday() < 5:
                        dates.append(current_date)
                    current_date += timedelta(days=1)

        return dates


if __name__ == "__main__":
    dates = OccurrenceUtils._dates_for_recurrence(
        WeekDay.WEDNESDAY.value,
        Recurrence.MONTHLY,
        date(2024, 6, 30),
        date(2024, 12, 7),
        MonthWeek.LAST.value,
    )
    print(dates)
