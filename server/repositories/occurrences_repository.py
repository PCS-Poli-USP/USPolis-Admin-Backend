from sqlmodel import Session

from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.schedule_db_model import Schedule
from server.utils.occurrence_utils import OccurrenceUtils


class OccurencesRepository:
    @staticmethod
    def allocate_schedule(
        schedule: Schedule, classroom: Classroom, session: Session
    ) -> None:
        occurrences = OccurrenceUtils.occurrences_from_schedules(schedule)
        schedule.occurrences = occurrences
        classroom.occurrences = occurrences

        schedule.allocated = True
        session.add(schedule)
        session.add(classroom)

    @staticmethod
    def allocate_class(class_: Class, classroom: Classroom, session: Session) -> None:
        for schedule in class_.schedules:
            OccurencesRepository.allocate_schedule(schedule, classroom, session)
        session.add(class_)  # TODO: checar se é necessário
