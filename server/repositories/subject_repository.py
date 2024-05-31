from fastapi import HTTPException, status
from sqlmodel import Session, col, select

from server.models.database.subject_db_model import Subject
from server.models.http.requests.subject_request_models import (
    SubjectRegister,
    SubjectUpdate,
)
from server.repositories.department_repository import DepartmentRepository


class SubjectRepository:
    @staticmethod
    def get_all(*, session: Session) -> list[Subject]:
        statement = select(Subject)
        subjects = session.exec(statement).all()
        return list(subjects)

    @staticmethod
    def get_by_id(*, id: int, session: Session) -> Subject:
        statement = select(Subject).where(col(Subject.id) == id)
        subject = session.exec(statement).first()
        if subject is None:
            raise SubjectNotExists(str(id))
        return subject

    @staticmethod
    def get_by_ids(*, ids: list[int], session: Session) -> list[Subject]:
        statement = select(Subject).where(col(Subject.id).in_(ids))
        subjects = session.exec(statement).all()
        return list(subjects)

    @staticmethod
    def create(*, input: SubjectRegister, session: Session) -> Subject:
        department = DepartmentRepository.get_by_id(
            id=input.department_id, session=session
        )
        new_subject = Subject(
            department=department,
            name=input.name,
            code=input.code,
            professors=input.professors,
            type=input.type,
            class_credit=input.class_credit,
            work_credit=input.work_credit,
            activation=input.activation,
            desactivation=input.desactivation,
        )
        session.add(new_subject)
        session.commit()
        session.refresh(new_subject)
        return new_subject

    @staticmethod
    def update(*, id: int, input: SubjectUpdate, session: Session) -> Subject:
        subject = SubjectRepository.get_by_id(id=id, session=session)
        if input.department_id is not None:
            department = DepartmentRepository.get_by_id(
                id=input.department_id, session=session
            )
            subject.department = department
        subject.name = input.name
        subject.code = input.code
        subject.professors = input.professors
        subject.type = input.type
        subject.class_credit = input.class_credit
        subject.work_credit = input.work_credit
        subject.activation = input.activation
        subject.desactivation = input.desactivation
        session.add(subject)
        session.commit()
        return subject

    @staticmethod
    def delete(*, id: int, session: Session) -> None:
        subject = SubjectRepository.get_by_id(id=id, session=session)
        session.delete(subject)
        session.commit()


class SubjectNotExists(HTTPException):
    def __init__(self, subject_info: str) -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND, f"Subject {subject_info} not exists"
        )
