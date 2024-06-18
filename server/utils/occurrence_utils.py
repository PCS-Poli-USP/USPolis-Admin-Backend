from datetime import date, timedelta

from server.models.database.occurrence_db_model import Occurrence
from server.models.database.schedule_db_model import Schedule
from server.utils.enums.recurrence import Recurrence


class OccurrenceUtils:
    # TODO: dont create occurrences on holidays
    # update/delete schedules
    @staticmethod
    def occurrences_from_schedules(schedule: Schedule) -> list[Occurrence]:
        occurrences: list[Occurrence] = []
        dates = OccurrenceUtils.__dates_for_recurrence(
            schedule.week_day.value,
            schedule.recurrence,
            schedule.start_date,
            schedule.end_date,
            schedule.month_week,
        )
        for occ_date in dates:
            occurrence = Occurrence(
                date=occ_date,
                start_time=schedule.start_time,
                end_time=schedule.end_time,
                schedule_id=schedule.id,
            )
            occurrences.append(occurrence)
        return occurrences

    @staticmethod
    def __dates_for_recurrence(
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
                first_month_day = date(start_date.year, start_date.month, 1)
                while True:
                    days_to_first_weekday = (
                        week_day - first_month_day.weekday() + 7
                    ) % 7
                    first_weekday_date = first_month_day + timedelta(
                        days=days_to_first_weekday
                    )
                    current_date = first_weekday_date + timedelta(days=7) * (
                        month_week - 1
                    )

                    if current_date > end_date:
                        break

                    dates.append(current_date)

                    if first_month_day.month == 12:
                        first_month_day = date(first_month_day.year + 1, 1, 1)
                    else:
                        first_month_day = date(
                            first_month_day.year, first_month_day.month + 1, 1
                        )

            case Recurrence.DAILY:
                current_date = start_date
                while current_date <= end_date:
                    if current_date.weekday() < 5:
                        dates.append(current_date)
                    current_date += timedelta(days=1)

        return dates


if __name__ == "__main__":
    dates = OccurrenceUtils.__dates_for_recurrence(
        2, Recurrence.MONTHLY, date(2024, 1, 1), date(2024, 3, 15), 2
    )
    print(dates)
