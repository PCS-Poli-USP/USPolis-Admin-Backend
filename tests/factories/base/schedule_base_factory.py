from datetime import time
from server.models.dicts.base.schedule_base_dict import ScheduleBaseDict
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.recurrence import Recurrence
from tests.factories.base.base_factory import BaseFactory


class ScheduleBaseFactory(BaseFactory):
    def __init__(self) -> None:
        super().__init__()
        self.start_times = [time(i, 0) for i in range(8, 22, 2)]
        self.end_times = [time(i, 0) for i in range(10, 24, 2)]

    def get_base_defaults(self) -> ScheduleBaseDict:
        index = self.faker.random_int(0, len(self.start_times) - 1)
        semester = BrazilDatetime.current_semester()
        return {
            "start_date": semester[0].date(),
            "end_date": semester[1].date(),
            "start_time": self.start_times[index],
            "end_time": self.end_times[index],
            "recurrence": Recurrence.WEEKLY,
            "all_day": False,
            "allocated": False,
        }
