from typing import Any
from fastapi import HTTPException, status
from sqlalchemy import Select, exists, and_
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, col, select

from server.deps.interval_dep import QueryInterval
from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.schedule_db_model import Schedule
from server.models.database.subject_building_link import SubjectBuildingLink
from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.models.http.requests.class_request_models import ClassRegister, ClassUpdate

from server.repositories.calendar_repository import CalendarRepository
from server.repositories.schedule_repository import ScheduleRepository
from server.repositories.subject_repository import SubjectRepository

from server.services.security.schedule_permission_checker import (
    SchedulePermissionChecker,
)
from server.utils.common_utils import compare_SQLModel_vectors_by_id
from server.utils.schedule_utils import ScheduleUtils


class ClassRepository:
    @staticmethod
    def __apply_interval_filter(
        *,
        statement: Select,
        interval: QueryInterval,
    ) -> Any:
        if interval.today:
            statement = statement.where(col(Class.end_date) >= interval.today)

        if interval.start and interval.end:
            statement = statement.where(
                col(Class.start_date) >= interval.start,
                col(Class.end_date) <= interval.end,
            )
        return statement

    @staticmethod
    def get_all(
        *,
        session: Session,
        interval: QueryInterval,
    ) -> list[Class]:
        """Get all classes of database."""
        statement = select(Class)
        statement = ClassRepository.__apply_interval_filter(
            statement=statement,
            interval=interval,
        )
        classes = session.exec(statement).all()
        return list(classes)

    @staticmethod
    def get_all_allocated_on_building(
        *,
        building_id: int,
        session: Session,
        interval: QueryInterval,
    ) -> list[Class]:
        statement = (
            select(Class)
            .join(Schedule)
            .join(Classroom)
            .where(col(Classroom.building_id) == (building_id))
            .distinct()  # avoid duplicates
        )
        statement = ClassRepository.__apply_interval_filter(
            statement=statement,
            interval=interval,
        )
        classes = session.exec(statement).all()
        return list(classes)

    @staticmethod
    def get_all_unallocated_on_buildings(
        *,
        building_ids: list[int],
        session: Session,
        interval: QueryInterval,
    ) -> list[Class]:
        """Get all classes that are not allocated in all schedules and are in one of the buildings."""
        # Query to get all schedules allocated for the class
        subquery = select(Schedule.id).where(
            and_(col(Schedule.class_id) == Class.id, col(Schedule.allocated))
        )
        statement = (
            select(Class)
            .join(Subject)
            .join(SubjectBuildingLink)
            .where(
                col(SubjectBuildingLink.building_id).in_(building_ids),
                ~exists(subquery),
            )
            .distinct()  # avoid duplicates
        )
        statement = ClassRepository.__apply_interval_filter(
            statement=statement,
            interval=interval,
        )
        classes = session.exec(statement).all()
        return list(classes)

    @staticmethod
    def get_all_on_classrooms(
        *,
        classroom_ids: list[int],
        session: Session,
        interval: QueryInterval,
    ) -> list[Class]:
        """Get all classes that are in one of his schedules are in classrooms_ids."""
        subquery = select(Schedule.id).where(
            and_(
                col(Schedule.class_id) == Class.id,
                col(Schedule.classroom_id).in_(classroom_ids),
            )
        )
        statement = select(Class).where(exists(subquery))
        statement = ClassRepository.__apply_interval_filter(
            statement=statement,
            interval=interval,
        )
        classes = session.exec(statement).all()
        return list(classes)

    @staticmethod
    def get_all_on_buildings(
        *,
        building_ids: list[int],
        session: Session,
        interval: QueryInterval,
    ) -> list[Class]:
        statement = (
            select(Class)
            .join(Subject)
            .join(SubjectBuildingLink)
            .where(col(SubjectBuildingLink.building_id).in_(building_ids))
            .distinct()  # avoid duplicates
        )
        statement = ClassRepository.__apply_interval_filter(
            statement=statement,
            interval=interval,
        )
        classes = session.exec(statement).all()
        return list(classes)

    @staticmethod
    def get_all_on_subject(
        *,
        subject_id: int,
        session: Session,
        interval: QueryInterval,
    ) -> list[Class]:
        """Get all classes of a subject."""
        statement = (
            select(Class)
            .join(Subject)
            .where(col(Subject.id) == subject_id)
            .distinct()  # avoid duplicates
        )
        statement = ClassRepository.__apply_interval_filter(
            statement=statement,
            interval=interval,
        )
        classes = session.exec(statement).all()
        return list(classes)

    @staticmethod
    def get_all_allocated_by_subjects(
        *,
        subject_ids: list[int],
        session: Session,
        interval: QueryInterval,
    ) -> list[Class]:
        subquery = (
            select(Schedule.id)
            .where(col(Schedule.class_id) == col(Class.id))
            .where(col(Schedule.allocated) == False)  # noqa: E712
        )
        statement = (
            select(Class)
            .where(col(Class.subject_id).in_(subject_ids))
            .where(~exists(subquery))
            .distinct()
        )  # avoid duplicates

        statement = ClassRepository.__apply_interval_filter(
            statement=statement,
            interval=interval,
        )
        classes = session.exec(statement).all()
        return list(classes)

    @staticmethod
    def get_by_id(*, id: int, session: Session) -> Class:
        statement = select(Class).where(col(Class.id) == id)
        try:
            class_ = session.exec(statement).one()
        except NoResultFound:
            raise ClassNotFound()
        return class_

    @staticmethod
    def get_by_ids(*, ids: list[int], session: Session) -> list[Class]:
        statement = select(Class).where(col(Class.id).in_(ids))
        classes = session.exec(statement).all()
        return list(classes)

    @staticmethod
    def get_by_id_on_building(id: int, building: Building, session: Session) -> Class:
        statement = select(Class).where(col(Class.id) == id)
        try:
            class_ = session.exec(statement).one()
        except NoResultFound:
            raise ClassNotFound()

        if building not in class_.subject.buildings:
            raise ClassNotFound()

        return class_

    @staticmethod
    def get_by_id_on_buildings(
        id: int, building_ids: list[int], session: Session
    ) -> Class:
        statement = (
            select(Class)
            .join(Subject, col(Class.subject_id) == col(Subject.id))
            .join(
                SubjectBuildingLink,
                col(Subject.id) == col(SubjectBuildingLink.subject_id),
            )
            .where(col(SubjectBuildingLink.building_id).in_(building_ids))
            .where(col(Class.id) == id)
            .distinct()
        )
        try:
            class_ = session.exec(statement).one()
        except NoResultFound:
            raise ClassNotFound()
        return class_

    @staticmethod
    def create(*, input: ClassRegister, session: Session) -> Class:
        subject = SubjectRepository.get_by_id(id=input.subject_id, session=session)
        calendars = (
            CalendarRepository.get_by_ids(ids=input.calendar_ids, session=session)
            if input.calendar_ids
            else None
        )
        new_class = Class(
            subject=subject,
            calendars=calendars if calendars else [],
            start_date=input.start_date,
            end_date=input.end_date,
            code=input.code,
            professors=input.professors,
            type=input.type,
            vacancies=input.vacancies,
            air_conditionating=input.air_conditionating,
            accessibility=input.accessibility,
            audiovisual=input.audiovisual,
            ignore_to_allocate=input.ignore_to_allocate,
            full_allocated=False,
        )
        schedules = ScheduleRepository.create_many_with_class(
            class_=new_class, input=input.schedules_data, session=session
        )
        new_class.schedules = schedules
        session.add(new_class)
        return new_class

    @staticmethod
    def __update_class_calendars(
        *,
        class_: Class,
        input: ClassUpdate,
        session: Session,
    ) -> bool:
        reallocate = False
        if input.calendar_ids:
            calendars = CalendarRepository.get_by_ids(
                ids=input.calendar_ids, session=session
            )
            # Only switch calendars if not exists or are different
            if class_.calendars:
                if not compare_SQLModel_vectors_by_id(calendars, class_.calendars):
                    class_.calendars = calendars
                    reallocate = True
            else:
                class_.calendars = calendars
                reallocate = True
        else:
            if len(class_.calendars) != 0:
                reallocate = True
            class_.calendars = []

        return reallocate

    @staticmethod
    def update(*, id: int, input: ClassUpdate, user: User, session: Session) -> Class:
        updated_class = ClassRepository.get_by_id(id=id, session=session)
        input_data = input.model_dump()
        for key, value in input_data.items():
            if hasattr(updated_class, key):
                setattr(updated_class, key, value)

        subject = SubjectRepository.get_by_id(id=input.subject_id, session=session)
        updated_class.subject = subject

        reallocate = ClassRepository.__update_class_calendars(
            class_=updated_class, input=input, session=session
        )

        # Only change schedules if is necessary (change calendars or change schedules)
        should_update = reallocate or ScheduleUtils.has_schedule_diff_from_list(
            updated_class.schedules, input.schedules_data
        )
        if should_update:
            checker = SchedulePermissionChecker(user=user, session=session)
            checker.check_permission(object=updated_class.schedules)
            updated_class.schedules = ScheduleRepository.update_class_schedules(
                class_=updated_class,
                input=input.schedules_data,
                user=user,
                session=session,
            )

        return updated_class

    @staticmethod
    def delete(*, id: int, session: Session) -> None:
        deleted_class = ClassRepository.get_by_id(id=id, session=session)
        session.delete(deleted_class)

    @staticmethod
    def delete_many(*, ids: list[int], session: Session) -> None:
        classes = ClassRepository.get_by_ids(ids=ids, session=session)
        for class_ in classes:
            session.delete(class_)


class ClassNotFound(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail="Turma não encontrada"
        )
