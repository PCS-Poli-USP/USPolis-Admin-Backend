from sqlmodel import Session

from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.occurrence_db_model import Occurrence
from server.models.database.schedule_db_model import Schedule
from server.models.http.exceptions.responses_exceptions import UnfetchDataError
from server.models.http.requests.occurrence_request_models import (
    OccurenceManyRegister,
    OccurrenceRegister,
)
from server.repositories.classroom_repository import ClassroomRepository
from server.utils.occurrence_utils import OccurrenceUtils


class OccurrenceRepository:
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

        schedule.classroom = classroom

        schedule.allocated = True

        session.add(schedule)
        session.add(classroom)

    @staticmethod
    def allocate_class(class_: Class, classroom: Classroom, session: Session) -> None:
        for schedule in class_.schedules:
            OccurrenceRepository.allocate_schedule(schedule, classroom, session)

    @staticmethod
    def remove_schedule_allocation(schedule: Schedule, session: Session) -> None:
        for occurrence in schedule.occurrences:
            session.delete(occurrence)
        schedule.allocated = False
        session.add(schedule)

    @staticmethod
    def remove_class_allocation(class_: Class, session: Session) -> None:
        for schedule in class_.schedules:
            OccurrenceRepository.remove_schedule_allocation(schedule, session)

    @staticmethod
    def create_with_schedule(
        *, schedule: Schedule, input: OccurrenceRegister, session: Session
    ) -> Occurrence:
        classroom = None
        if input.classroom_id:
            classroom = ClassroomRepository.get_by_id(
                id=input.classroom_id, session=session
            )
        occurrence = Occurrence(
            schedule_id=input.schedule_id,
            schedule=schedule,
            classroom_id=input.classroom_id,
            classroom=classroom,
            start_time=input.start_time,
            end_time=input.end_time,
            date=input.date,
        )
        session.add(occurrence)
        session.commit()
        session.refresh(occurrence)
        return occurrence

    @staticmethod
    def create_many_with_schedule(
        *, schedule: Schedule, input: OccurenceManyRegister, session: Session
    ) -> list[Occurrence]:
        classroom = None
        if input.classroom_id is not None:
            classroom = ClassroomRepository.get_by_id(
                id=input.classroom_id, session=session
            )

        if schedule.id is None:
            raise UnfetchDataError("Schedule", "ID")

        occurrences: list[Occurrence] = []
        for date in input.dates:
            occurrence = Occurrence(
                schedule_id=schedule.id,
                schedule=schedule,
                classroom_id=input.classroom_id,
                classroom=classroom,
                start_time=input.start_time,
                end_time=input.end_time,
                date=date,
            )
            session.add(occurrence)
            session.commit()
            session.refresh(occurrence)
            occurrences.append(occurrence)
        return occurrences
