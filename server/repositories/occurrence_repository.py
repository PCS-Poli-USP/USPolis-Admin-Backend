from datetime import date
from sqlmodel import Session, col, select

from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.occurrence_db_model import Occurrence
from server.models.database.schedule_db_model import Schedule
from server.models.database.user_db_model import User
from server.models.http.requests.allocation_log_request_models import AllocationLogInput
from server.models.http.requests.occurrence_request_models import (
    OccurenceManyRegister,
    OccurrenceRegister,
)
from server.repositories.allocation_log_repository import AllocationLogRepository
from server.utils.enums.recurrence import Recurrence
from server.utils.occurrence_utils import OccurrenceUtils


class OccurrenceRepository:
    @staticmethod
    def get_by_id(id: int, session: Session) -> Occurrence:
        statement = select(Occurrence).where(col(Occurrence.id) == id)
        occurrence = session.exec(statement).one()
        return occurrence

    @staticmethod
    def get_by_ids(ids: list[int], session: Session) -> list[Occurrence]:
        statement = (
            select(Occurrence)
            .where(col(Occurrence.id).in_(ids))
            .order_by(col(Occurrence.date))
        )
        occurrences = session.exec(statement).all()
        return list(occurrences)

    @staticmethod
    def get_by_date_and_classroom(
        date: date, classroom_id: int, session: Session
    ) -> list[Occurrence]:
        statement = select(Occurrence).where(
            col(Occurrence.date) == date,
            col(Occurrence.classroom_id) == classroom_id,
        )
        occurrences = session.exec(statement).all()
        return list(occurrences)

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
    def get_all_on_interval(
        start: date, end: date, session: Session
    ) -> list[Occurrence]:
        statement = select(Occurrence).where(
            Occurrence.date >= start, Occurrence.date <= end
        )
        occurrences = session.exec(statement).all()
        return list(occurrences)

    @staticmethod
    def get_all_on_interval_for_classroom(
        classroom_id: int, start: date, end: date, session: Session
    ) -> list[Occurrence]:
        """Get all occurrences on interval for classroom"""
        statement = select(Occurrence).where(
            Occurrence.date >= start,
            Occurrence.date <= end,
            Occurrence.classroom_id == classroom_id,
        )
        occurrences = session.exec(statement).all()
        return list(occurrences)

    @staticmethod
    def allocate_occurrence(
        occurrence: Occurrence, classroom: Classroom, session: Session
    ) -> None:
        occurrence.classroom_id = classroom.id
        occurrence.classroom = classroom
        classroom.occurrences.append(occurrence)
        session.add(occurrence)
        session.add(classroom)

    @staticmethod
    def allocate_schedule(
        user: User,
        schedule: Schedule,
        classroom: Classroom,
        session: Session,
    ) -> list[Occurrence]:
        input = AllocationLogInput.for_allocation(
            user=user, schedule=schedule, classroom=classroom
        )
        AllocationLogRepository.create(input=input, schedule=schedule, session=session)
        occurrences = OccurrenceUtils.generate_occurrences(schedule)
        if schedule.allocated:
            previous_occurrences = schedule.occurrences
            for occurrence in previous_occurrences:
                session.delete(occurrence)
            schedule.occurrences = occurrences

        for occurrence in occurrences:
            occurrence.classroom_id = classroom.id
            occurrence.classroom = classroom
            session.add(occurrence)

        schedule.classroom = classroom
        schedule.allocated = True
        session.add(schedule)
        session.add(classroom)
        return occurrences

    @staticmethod
    def remove_occurrence_allocation(occurrence: Occurrence, session: Session) -> None:
        occurrence.classroom = None
        occurrence.classroom_id = None
        session.add(occurrence)

    @staticmethod
    def remove_schedule_allocation(
        user: User, schedule: Schedule, session: Session
    ) -> None:
        input = AllocationLogInput.for_deallocation(user=user, schedule=schedule)
        AllocationLogRepository.create(input=input, schedule=schedule, session=session)
        if schedule.recurrence != Recurrence.CUSTOM:
            for occurrence in schedule.occurrences:
                session.delete(occurrence)
        else:
            for occurrence in schedule.occurrences:
                occurrence.classroom = None
                occurrence.classroom_id = None
                session.add(occurrence)
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
        for dt in input.dates:
            occurrence = Occurrence(
                schedule=schedule,
                classroom_id=input.classroom_id,
                classroom=classroom,
                start_time=input.start_time,
                end_time=input.end_time,
                date=dt,
            )
            session.add(occurrence)
            occurrences.append(occurrence)
        return occurrences
