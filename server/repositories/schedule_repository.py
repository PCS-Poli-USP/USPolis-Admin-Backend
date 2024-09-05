from fastapi import HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, col, select

from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.classroom_solicitation_db_model import ClassroomSolicitation
from server.models.database.occurrence_db_model import Occurrence
from server.models.database.reservation_db_model import Reservation
from server.models.database.schedule_db_model import Schedule
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
        schedule = session.exec(statement).one()
        return schedule

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
        schedule = session.exec(statement).one()
        return schedule

    @staticmethod
    def get_by_id_on_buildings(
        *, schedule_id: int, owned_building_ids: list[int], session: Session
    ) -> Schedule:
        statement = select(Schedule).where(Schedule.id == schedule_id)

        try:
            schedule = session.exec(statement).one()
        except NoResultFound:
            raise ScheduleNotFound()

        if schedule.class_:
            buildings = schedule.class_.subject.buildings
            building_ids = [building.id for building in buildings]
            if not set(building_ids).issubset(set(owned_building_ids)):
                raise ScheduleNotFound()
        elif schedule.reservation:
            building = schedule.reservation.classroom.building
            if building.id not in owned_building_ids:
                raise ScheduleNotFound()

        return schedule

    @staticmethod
    def create_with_class(
        *, class_input: Class, input: ScheduleRegister, session: Session
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
            class_id=class_input.id,
            class_=class_input,
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
        reservation: Reservation,
        input: ScheduleRegister,
        classroom: Classroom,
        session: Session,
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
            class_id=None,
            class_=None,
            reservation_id=reservation.id,
            reservation=reservation,
            classroom_id=input.classroom_id,
        )

        if input.dates and input.recurrence == Recurrence.CUSTOM:
            occurences_input = OccurenceManyRegister(
                classroom_id=classroom.id,
                start_time=input.start_time,
                end_time=input.end_time,
                dates=input.dates,
            )
            occurences = OccurrenceRepository.create_many_with_schedule(
                schedule=new_schedule, input=occurences_input, session=session
            )
            new_schedule.occurrences = occurences
            session.add(new_schedule)
        else:
            # schedule is add to sesion here
            OccurrenceRepository.allocate_schedule(
                schedule=new_schedule, classroom=classroom, session=session
            )
        return new_schedule

    @staticmethod
    def create_with_reservation_and_solicitation(
        reservation: Reservation, solicitation: ClassroomSolicitation, session: Session
    ) -> Schedule:
        new_schedule = Schedule(
            start_date=solicitation.date,
            end_date=solicitation.date,
            recurrence=Recurrence.CUSTOM,
            month_week=None,
            all_day=False,
            allocated=True,
            week_day=None,
            start_time=solicitation.start_time,
            end_time=solicitation.end_time,
            class_id=None,
            class_=None,
            reservation_id=reservation.id,
            reservation=reservation,
            classroom_id=solicitation.classroom_id,
        )
        occurrences_input = OccurenceManyRegister(
            classroom_id=solicitation.classroom_id,
            start_time=solicitation.start_time,
            end_time=solicitation.end_time,
            dates=[solicitation.date],
        )
        occurrences = OccurrenceRepository.create_many_with_schedule(
            schedule=new_schedule, input=occurrences_input, session=session
        )
        new_schedule.occurrences = occurrences
        session.add(new_schedule)
        return new_schedule

    @staticmethod
    def create_many_with_class(
        *, university_class: Class, input: list[ScheduleRegister], session: Session
    ) -> list[Schedule]:
        return [
            ScheduleRepository.create_with_class(
                class_input=university_class, input=schedule_input, session=session
            )
            for schedule_input in input
        ]

    @staticmethod
    def update_class_schedules(
        *, class_: Class, input: list[ScheduleUpdate], session: Session
    ) -> list[Schedule]:
        """ """
        for schedule in class_.schedules:
            session.delete(schedule)

        new_schedules = []
        for schedule_input in input:
            new_schedule = ScheduleRepository.create_with_class(
                class_input=class_, input=schedule_input, session=session
            )
            if schedule_input.allocated and schedule_input.classroom_id:
                classroom = ClassroomRepository.get_by_id(
                    id=schedule_input.classroom_id, session=session
                )
                OccurrenceRepository.allocate_schedule(
                    schedule=new_schedule, classroom=classroom, session=session
                )
            new_schedules.append(new_schedule)

        return new_schedules

    @staticmethod
    def update_reservation_schedule(
        *,
        reservation: Reservation,
        input: ScheduleUpdate,
        classroom: Classroom,
        session: Session,
    ) -> Schedule:
        old_schedule = reservation.schedule

        if ScheduleUtils.has_schedule_diff(old_schedule, input):
            session.delete(old_schedule)
            new_schedule = ScheduleRepository.create_with_reservation(
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


class ScheduleInvalidData(HTTPException):
    def __init__(self, schedule_info: str, data_info: str) -> None:
        super().__init__(
            status.HTTP_400_BAD_REQUEST,
            f"Schedule with {schedule_info} has invalid {data_info} value",
        )


class ScheduleNotFound(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found"
        )
