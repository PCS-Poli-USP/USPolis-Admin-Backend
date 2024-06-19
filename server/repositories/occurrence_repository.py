from sqlmodel import Session
from server.models.database.occurrence_db_model import Occurrence
from server.models.database.schedule_db_model import Schedule
from server.models.http.exceptions.responses_exceptions import UnfetchDataError
from server.models.http.requests.occurrence_request_models import (
    OccurenceManyRegister,
    OccurrenceRegister,
)
from server.repositories.classrooms_repository import ClassroomRepository


class OccurrenceRepository:
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
