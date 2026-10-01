from server.models.dicts.base.user_schedule_base_dict import UserScheduleBaseDict
from server.utils.brazil_datetime import BrazilDatetime
from tests.factories.base.base_factory import BaseFactory


class UserScheduleBaseFactory(BaseFactory):
    def __init__(self) -> None:
        super().__init__()

    def get_base_defaults(self) -> UserScheduleBaseDict:
        semester = BrazilDatetime.current_semester()
        return {
            "start_date": semester[0].date(),
            "end_date": semester[1].date(),
        }
