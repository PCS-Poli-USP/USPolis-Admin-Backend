from fastapi import HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, col, select

from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.subject_building_link import SubjectBuildingLink
from server.models.database.subject_db_model import Subject
from server.models.http.requests.class_request_models import ClassRegister, ClassUpdate
from server.repositories.calendar_repository import CalendarRepository
from server.repositories.schedule_repository import ScheduleRepository
from server.repositories.subject_repository import SubjectRepository

from server.utils.common_utils import compare_SQLModel_vectors_by_id


class ClassRepository:
    @staticmethod
    def get_all(*, session: Session) -> list[Class]:
        statement = select(Class)
        classes = session.exec(statement).all()
        return list(classes)

    @staticmethod
    def get_all_on_buildings(
        *, building_ids: list[int], session: Session
    ) -> list[Class]:
        statement = (
            select(Class)
            .join(Subject)
            .join(SubjectBuildingLink)
            .where(col(SubjectBuildingLink.building_id).in_(building_ids))
            .distinct() # avoid duplicates
        )
        classes = session.exec(statement).all()
        return list(classes)

    @staticmethod
    def get_by_id(*, id: int, session: Session) -> Class:
        statement = select(Class).where(col(Class.id) == id)
        _class = session.exec(statement).one()
        return _class

    @staticmethod
    def get_by_id_on_building(id: int, building: Building, session: Session) -> Class:
        statement = select(Class).where(col(Class.id) == id)
        class_ = session.exec(statement).one()

        if building not in class_.subject.buildings:
            raise ClassNotFound()

        return class_

    @staticmethod
    def get_by_id_on_buildings(
        id: int, building_ids: list[int], session: Session
    ) -> Class:
        statement = (
            select(Class)
            .join(Subject)
            .join(SubjectBuildingLink)
            .where(col(SubjectBuildingLink.building_id).in_(building_ids))
            .where(col(Class.id) == id)
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
            subscribers=input.subscribers,
            pendings=input.pendings,
            air_conditionating=input.air_conditionating,
            accessibility=input.accessibility,
            projector=input.projector,
            ignore_to_allocate=input.ignore_to_allocate,
            full_allocated=False,
        )
        schedules = ScheduleRepository.create_many_with_class(
            university_class=new_class, input=input.schedules_data, session=session
        )
        new_class.schedules = schedules
        session.add(new_class)
        return new_class

    @staticmethod
    def update(*, id: int, input: ClassUpdate, session: Session) -> Class:
        updated_class = ClassRepository.get_by_id(id=id, session=session)
        input_data = input.model_dump()
        for key, value in input_data.items():
            if hasattr(updated_class, key):
                setattr(updated_class, key, value)

        if input.subject_id:
            subject = SubjectRepository.get_by_id(id=input.subject_id, session=session)
            updated_class.subject = subject

        if input.calendar_ids:
            calendars = CalendarRepository.get_by_ids(
                ids=input.calendar_ids, session=session
            )
            # Only switch calendars if not exists or are different
            if updated_class.calendars:
                if not compare_SQLModel_vectors_by_id(
                    calendars, updated_class.calendars
                ):
                    updated_class.calendars = calendars
            else:
                updated_class.calendars = calendars

        if input.schedules_data:
            new_schedules = ScheduleRepository.update_class_schedules(
                class_=updated_class, input=input.schedules_data, session=session
            )
            updated_class.schedules = new_schedules

        session.add(updated_class)
        return updated_class

    @staticmethod
    def delete(*, id: int, session: Session) -> None:
        deleted_class = ClassRepository.get_by_id(id=id, session=session)
        session.delete(deleted_class)

    @staticmethod
    def delete_many(*, ids: list[int], session: Session) -> None:
        statement = select(Class).where(col(Class.id).in_(ids))
        classes = session.exec(statement).all()
        for class_ in classes:
            session.delete(class_)


class ClassNotFound(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail="Class not found"
        )
