from datetime import date as datetime_date
from fastapi import HTTPException, status

# from sqlalchemy import func
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, col, select

from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.occurrence_db_model import Occurrence
from server.models.database.reservation_db_model import Reservation
from server.models.database.schedule_db_model import Schedule
from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.models.http.requests.occurrence_request_models import OccurenceManyRegister
from server.models.http.requests.schedule_request_models import (
    ScheduleRegister,
    ScheduleUpdate,
    ScheduleUpdateOccurrences,
)
from server.repositories.classroom_repository import ClassroomRepository
from server.repositories.occurrence_repository import OccurrenceRepository
from server.utils.enums.recurrence import Recurrence
from server.utils.schedule_utils import ScheduleUtils


class ScheduleRepository:
    @staticmethod
    def get_all(*, session: Session) -> list[Schedule]:
        statement = select(Schedule)
        schedules = session.exec(statement).all()
        return list(schedules)

    @staticmethod
    def get_by_id(*, id: int, session: Session) -> Schedule:
        statement = select(Schedule).where(col(Schedule.id) == id)
        try:
            schedule = session.exec(statement).one()
        except NoResultFound:
            raise ScheduleNotFound()
        return schedule

    @staticmethod
    def get_all_unallocated(*, session: Session) -> list[Schedule]:
        statement = select(Schedule).where(Schedule.allocated == False)  # noqa: E712
        schedules = session.exec(statement).all()
        return list(schedules)

    @staticmethod
    def get_all_on_class(*, class_: Class, session: Session) -> list[Schedule]:
        statement = select(Schedule).where(Schedule.class_id == class_.id)
        schedules = list(session.exec(statement).all())
        return schedules

    @staticmethod
    def get_by_id_on_class(*, class_: Class, id: int, session: Session) -> Schedule:
        statement = (
            select(Schedule)
            .where(Schedule.class_id == class_.id)
            .where(Schedule.id == id)
        )
        try:
            schedule = session.exec(statement).one()
        except NoResultFound:
            raise ScheduleNotFound()
        return schedule

    @staticmethod
    def get_by_id_on_buildings(
        *, schedule_id: int, owned_building_ids: list[int], session: Session
    ) -> Schedule:
        schedule = ScheduleRepository.get_by_id(id=schedule_id, session=session)

        if schedule.class_:
            buildings = schedule.class_.subject.buildings
            building_ids = [building.id for building in buildings]
            if len(set(building_ids).intersection(set(owned_building_ids))) == 0:
                raise ScheduleNotFound()
        elif schedule.reservation:
            building = schedule.reservation.get_building()
            if building.id not in owned_building_ids:
                raise ScheduleNotFound()

        return schedule

    @staticmethod
    def find_old_allocation_options(
        *, building_id: int, year: int, target: Schedule, session: Session
    ) -> list[Schedule]:
        """Get all schedules that can be reused for allocation"""
        if not target.class_:
            raise InvalidScheduleAllocationReuseTarget()
        # class_number = target.class_.code[-2:]
        start = datetime_date(year, 1, 1)
        end = datetime_date(year, 12, 31)
        statement = (
            select(Schedule)
            .join(Class)
            .join(Subject)
            .where(
                Schedule.start_date >= start,
                Schedule.end_date <= end,
                Schedule.week_day == target.week_day,
                Schedule.month_week == target.month_week,
                Schedule.recurrence == target.recurrence,
                Schedule.start_time == target.start_time,
                Schedule.end_time == target.end_time,
                # func.right(Class.code, 2) == class_number,
                col(Subject.code) == target.class_.subject.code,
            )
        )

        schedules = list(session.exec(statement).all())
        schedules = [
            schedule
            for schedule in schedules
            if (not schedule.classroom or schedule.classroom.building_id == building_id)
        ]
        return schedules

    @staticmethod
    def create_with_class(
        *, class_: Class, input: ScheduleRegister, session: Session
    ) -> Schedule:
        new_schedule = Schedule(
            start_date=input.start_date,
            end_date=input.end_date,
            recurrence=input.recurrence,
            month_week=input.month_week,
            all_day=input.all_day,
            allocated=input.allocated if input.allocated else False,
            week_day=input.week_day,
            start_time=input.start_time,
            end_time=input.end_time,
            class_id=class_.id,
            class_=class_,
            reservation_id=None,
            classroom_id=None,
        )

        if input.dates:
            occurences_input = OccurenceManyRegister(
                classroom_id=None,
                start_time=input.start_time,
                end_time=input.end_time,
                dates=input.dates,
            )
            occurences = OccurrenceRepository.create_many_with_schedule(
                schedule=new_schedule, input=occurences_input, session=session
            )
            new_schedule.occurrences = occurences

        session.add(new_schedule)
        return new_schedule

    @staticmethod
    def create_with_reservation(
        *,
        user: User,
        reservation: Reservation,
        input: ScheduleRegister,
        classroom: Classroom | None,
        session: Session,
        allocate: bool = True,
    ) -> Schedule:
        new_schedule = Schedule(
            start_date=input.start_date,
            end_date=input.end_date,
            recurrence=input.recurrence,
            month_week=input.month_week,
            all_day=input.all_day,
            allocated=input.allocated,
            week_day=input.week_day,
            start_time=input.start_time,
            end_time=input.end_time,
            class_id=None,
            class_=None,
            reservation_id=reservation.id,
            reservation=reservation,
            classroom_id=classroom.id if classroom else None,
        )

        if input.dates and input.recurrence == Recurrence.CUSTOM:
            occurences_input = OccurenceManyRegister(
                classroom_id=classroom.id if allocate and classroom else None,
                start_time=input.start_time,
                end_time=input.end_time,
                dates=input.dates,
            )
            occurences = OccurrenceRepository.create_many_with_schedule(
                schedule=new_schedule, input=occurences_input, session=session
            )
            new_schedule.occurrences = occurences
            if allocate:
                new_schedule.allocated = True
            session.add(new_schedule)
        else:
            if allocate and classroom:
                # schedule is add to sesion here
                OccurrenceRepository.allocate_schedule(
                    user=user,
                    schedule=new_schedule,
                    classroom=classroom,
                    session=session,
                )
            else:
                session.add(new_schedule)
        return new_schedule

    @staticmethod
    def create_many_with_class(
        *, class_: Class, input: list[ScheduleRegister], session: Session
    ) -> list[Schedule]:
        return [
            ScheduleRepository.create_with_class(
                class_=class_, input=schedule_input, session=session
            )
            for schedule_input in input
        ]

    @staticmethod
    def update_class_schedules(
        *, class_: Class, user: User, input: list[ScheduleUpdate], session: Session
    ) -> list[Schedule]:
        """ """
        for schedule in class_.schedules:
            session.delete(schedule)

        new_schedules = []
        for schedule_input in input:
            new_schedule = ScheduleRepository.create_with_class(
                class_=class_, input=schedule_input, session=session
            )
            if schedule_input.allocated and schedule_input.classroom_id:
                classroom = ClassroomRepository.get_by_id(
                    id=schedule_input.classroom_id, session=session
                )
                OccurrenceRepository.allocate_schedule(
                    user=user,
                    schedule=new_schedule,
                    classroom=classroom,
                    session=session,
                )
            new_schedules.append(new_schedule)

        return new_schedules

    @staticmethod
    def update_reservation_schedule(
        *,
        user: User,
        reservation: Reservation,
        input: ScheduleUpdate,
        classroom: Classroom,
        session: Session,
    ) -> Schedule:
        old_schedule = reservation.schedule

        should_reallocate = False
        if not old_schedule.classroom:
            should_reallocate = True
        if old_schedule.classroom and classroom.id != old_schedule.classroom.id:
            should_reallocate = True
        if ScheduleUtils.has_schedule_diff(old_schedule, input):
            should_reallocate = True

        if should_reallocate:
            session.delete(old_schedule)
            new_schedule = ScheduleRepository.create_with_reservation(
                user=user,
                reservation=reservation,
                input=input,
                classroom=classroom,
                session=session,
            )
            reservation.schedule = new_schedule
            return new_schedule

        return old_schedule

    @staticmethod
    def update_occurrences(
        *, id: int, input: ScheduleUpdateOccurrences, session: Session
    ) -> Schedule:
        """Update schedule occurrences withou commit the session"""
        schedule = ScheduleRepository.get_by_id(id=id, session=session)
        occurrences_by_date = {
            occurrence.date: occurrence for occurrence in schedule.occurrences
        }
        new_dates = set(input.dates)
        current_dates = set(occurrences_by_date.keys())
        dates_to_remove = current_dates - new_dates
        dates_to_add = new_dates - current_dates
        occurences_to_remove = [occurrences_by_date[date] for date in dates_to_remove]
        for occurrence in occurences_to_remove:
            session.delete(occurrence)

        for date in dates_to_add:
            new_occurrence = Occurrence(
                start_time=schedule.start_time,
                end_time=schedule.end_time,
                date=date,
                classroom=schedule.classroom,
                schedule=schedule,
            )
            session.add(new_occurrence)
        return schedule

    @staticmethod
    def delete(*, id: int, session: Session) -> None:
        schedule = ScheduleRepository.get_by_id(id=id, session=session)
        session.delete(schedule)
        return


class ScheduleNotFound(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agenda não encontrada"
        )


class InvalidScheduleAllocationReuseTarget(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agenda deve ser de uma turma para reutilização de alocação",
        )
