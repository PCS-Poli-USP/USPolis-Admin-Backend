from fastapi import HTTPException
from sqlmodel import Session, col, select

from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.http.requests.class_request_models import ClassRegister, ClassUpdate
from server.repositories.calendar_repository import CalendarRepository
from server.repositories.schedule_repository import ScheduleRepository
from server.repositories.subject_repository import SubjectRepository


class ClassRepository:
    @staticmethod
    def get_all(*, session: Session) -> list[Class]:
        statement = select(Class)
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
    def create(*, input: ClassRegister, session: Session) -> Class:
        subject = SubjectRepository.get_by_id(id=input.subject_id, session=session)
        calendars = CalendarRepository.get_by_ids(
            ids=input.calendar_ids, session=session
        ) if input.calendar_ids else None
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
        session.add(new_class)
        session.commit()
        session.refresh(new_class)

        schedules = ScheduleRepository.create_many_with_class(
            university_class=new_class, input=input.schedules_data, session=session
        )
        new_class.schedules = schedules
        session.add(new_class)
        session.commit()
        session.refresh(new_class)
        return new_class

    @staticmethod
    def update(*, id: int, input: ClassUpdate, session: Session) -> Class:
        updated_class = ClassRepository.get_by_id(id=id, session=session)
        input_data = input.model_dump(exclude_unset=True)
        for key, value in input_data.items():
            if hasattr(updated_class, key):
                setattr(updated_class, key, value)

        if input.subject_id:
            subject = SubjectRepository.get_by_id(id=input.subject_id, session=session)
            updated_class.subject = subject

        if input.schedules_data:
            pass  # TODO

        session.add(updated_class)
        session.commit()
        return updated_class

    @staticmethod
    def delete(*, id: int, session: Session) -> None:
        deleted_class = ClassRepository.get_by_id(id=id, session=session)
        session.delete(deleted_class)
        session.commit()


class ClassNotFound(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=404, detail="Class not found")
