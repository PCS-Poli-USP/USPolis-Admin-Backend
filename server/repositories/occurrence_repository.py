from typing import TYPE_CHECKING
from sqlmodel import Session, col, select

from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.occurrence_db_model import Occurrence
from server.models.database.schedule_db_model import Schedule
from server.models.http.requests.occurrence_request_models import (
    OccurenceManyRegister,
    OccurrenceRegister,
)
from server.utils.enums.recurrence import Recurrence
from server.utils.occurrence_utils import OccurrenceUtils


class OccurrenceRepository:
    @staticmethod
    def get_all_on_buildings(
        building_ids: list[int], session: Session
    ) -> list[Occurrence]:
        statement = (
            select(Occurrence)
            .join(Classroom)
            .join(Building)
            .where(col(Building.id).in_(building_ids))
        )
        buildings = session.exec(statement).all()
        return list(buildings)

    @staticmethod
    def allocate_schedule(
        schedule: Schedule, classroom: Classroom, session: Session
    ) -> None:
        occurrences = OccurrenceUtils.generate_occurrences(schedule)

        previous_occurrences = schedule.occurrences
        if previous_occurrences:
            for occurrence in previous_occurrences:
                session.delete(occurrence)

        schedule.occurrences = occurrences
        classroom.occurrences.extend(occurrences)

        schedule.classroom = classroom

        schedule.allocated = True

        session.add(schedule)
        session.add(classroom)

    @staticmethod
    def remove_schedule_allocation(schedule: Schedule, session: Session) -> None:
        if schedule.occurrences:
            if schedule.recurrence != Recurrence.CUSTOM:
                for occurrence in schedule.occurrences:
                    session.delete(occurrence)
            else:
                for occurrence in schedule.occurrences:
                    occurrence.classroom = None
        schedule.allocated = False
        schedule.classroom_id = None
        session.add(schedule)

    @staticmethod
    def create_with_schedule(
        *, schedule: Schedule, input: OccurrenceRegister, session: Session
    ) -> Occurrence:
        from server.repositories.classroom_repository import ClassroomRepository

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
        from server.repositories.classroom_repository import ClassroomRepository

        classroom = None
        if input.classroom_id is not None:
            classroom = ClassroomRepository.get_by_id(
                id=input.classroom_id, session=session
            )

        occurrences: list[Occurrence] = []
        for date in input.dates:
            occurrence = Occurrence(
                schedule=schedule,
                classroom_id=input.classroom_id,
                classroom=classroom,
                start_time=input.start_time,
                end_time=input.end_time,
                date=date,
            )
            session.add(occurrence)
            occurrences.append(occurrence)
        return occurrences
