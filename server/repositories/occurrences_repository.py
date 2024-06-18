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

        previous_occurrences = schedule.occurrences
        for occurrence in previous_occurrences:
            session.delete(occurrence)

        schedule.occurrences = occurrences
        classroom.occurrences.extend(occurrences)

        schedule.allocated = True
        
        session.add(schedule)
        session.add(classroom)

    @staticmethod
    def allocate_class(class_: Class, classroom: Classroom, session: Session) -> None:
        for schedule in class_.schedules:
            OccurencesRepository.allocate_schedule(schedule, classroom, session)
    
    @staticmethod
    def remove_schedule_allocation(schedule: Schedule, session: Session) -> None:
        for occurrence in schedule.occurrences:
            session.delete(occurrence)
        schedule.allocated = False
        session.add(schedule)

    @staticmethod
    def remove_class_allocation(class_: Class, session: Session) -> None:
        for schedule in class_.schedules:
            OccurencesRepository.remove_schedule_allocation(schedule, session)
