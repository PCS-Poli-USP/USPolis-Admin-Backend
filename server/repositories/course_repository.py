from fastapi import HTTPException
from sqlmodel import Session, select

from server.models.database.course_db_model import Course
from server.models.http.requests.course_request_models import (
    CourseRegister,
    CourseUpdate,
)
from server.models.database.user_db_model import User
from server.utils.must_be_int import must_be_int

class CourseRepository:

    @staticmethod
    def create(
        input: CourseRegister,
        user: User,
        session: Session,
    ) -> Course:
        course = Course(
            name=input.name,
            minimal_duration=input.minimal_duration,
            ideal_duration=input.ideal_duration,
            maximal_duration=input.maximal_duration,
            updated_by_id=must_be_int(user.id),
            created_by_id=must_be_int(user.id),
            period=input.period,
        )
        session.add(course)
        session.flush()
        return course


    @staticmethod
    def get_by_id(id: int, session: Session) -> Course | None:
        statement = select(Course).where(Course.id == id)
        return session.exec(statement).first()


    @staticmethod
    def get_all(session: Session) -> list[Course]:
        statement = select(Course)
        return list(session.exec(statement).all())


    @staticmethod
    def update(
        id: int,
        input: CourseUpdate,
        user: User,
        session: Session,
    ) -> Course:

        course = CourseRepository.get_by_id(id=id, session=session)

        if not course:
            raise HTTPException(404, "Curso não encontrado")

        course.name = input.name
        course.minimal_duration = input.minimal_duration
        course.ideal_duration = input.ideal_duration
        course.maximal_duration = input.maximal_duration
        course.updated_by_id = must_be_int(user.id)
        course.period = input.period

        session.add(course)
        session.flush()
        return course


    @staticmethod
    def delete(id: int, session: Session) -> None:

        course = CourseRepository.get_by_id(id=id, session=session)

        if not course:
            raise HTTPException(404, "Curso não encontrado")

        session.delete(course)
