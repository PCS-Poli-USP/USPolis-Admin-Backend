from sqlmodel import Session


from server.models.database.class_db_model import Class
from server.models.database.schedule_db_model import Schedule
from server.models.http.requests.schedule_request_models import ScheduleManyRegister


class ScheduleRepository:
    @staticmethod
    def create_many_from_class(
        *, university_class: Class, input: ScheduleManyRegister, session: Session
    ) -> list[Schedule]:
        return []
