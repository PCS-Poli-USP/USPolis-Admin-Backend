from server.models.database.schedule_db_model import Schedule
from server.models.http.requests.schedule_request_models import ScheduleUpdate


class ScheduleUtils:
    @staticmethod
    def sort_schedules(schedules: list[Schedule]) -> list[Schedule]:
        return sorted(
            schedules,
            key=lambda schedule: (
                schedule.recurrence.value,
                schedule.start_time,
                schedule.end_time,
            ),
        )

    @staticmethod
    def sort_schedules_input(
        schedules_inputs: list[ScheduleUpdate],
    ) -> list[ScheduleUpdate]:
        return sorted(
            schedules_inputs,
            key=lambda schedule: (
                schedule.recurrence.value,
                schedule.start_time,
                schedule.end_time,
            ),
        )

    @staticmethod
    def has_schedule_diff(schedule: Schedule, schedule_input: ScheduleUpdate) -> bool:
        if schedule.recurrence != schedule_input.recurrence:
            return True
        if schedule.week_day != schedule_input.week_day:
            return True
        if schedule.start_date != schedule_input.start_date:
            return True
        if schedule.end_date != schedule_input.end_date:
            return True
        if schedule.start_time != schedule_input.start_time:
            return True
        if schedule.end_time != schedule_input.end_time:
            return True
        if schedule_input.dates and schedule.occurrences:
            if len(schedule.occurrences) != len(schedule_input.dates):
                return True
            for i in range(len(schedule.occurrences)):
                if schedule.occurrences[i].date != schedule_input.dates[i]:
                    return True
        return False
