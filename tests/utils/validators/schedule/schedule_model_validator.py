from server.models.database.schedule_db_model import Schedule
from server.models.http.requests.schedule_request_models import ScheduleRegister


class ScheduleModelAsserts:
    @staticmethod
    def assert_schedule_after_create(
        schedule: Schedule, input: ScheduleRegister
    ) -> None:
        assert schedule.start_time == input.start_time
        assert schedule.end_time == input.end_time

    @staticmethod
    def assert_schedule_after_update(
        schedule: Schedule, input: ScheduleRegister
    ) -> None:
        assert schedule.start_time == input.start_time
        assert schedule.end_time == input.end_time
