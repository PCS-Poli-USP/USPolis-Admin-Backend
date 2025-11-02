from typing import Any
from fastapi import HTTPException, status
from sqlalchemy import Select
from sqlmodel import Session, col, select
from server.deps.interval_dep import QueryInterval
from server.models.database.exam_class_link import ExamClassLink
from server.models.database.exam_db_model import Exam
from server.models.database.reservation_db_model import Reservation
from server.models.database.schedule_db_model import Schedule
from server.models.database.user_db_model import User
from server.models.http.requests.exam_request_models import ExamRegister, ExamUpdate
from server.repositories.class_repository import ClassRepository
from server.repositories.classroom_repository import ClassroomRepository
from server.repositories.reservation_repository import ReservationRepository
from server.repositories.subject_repository import SubjectRepository
from server.utils.must_be_int import must_be_int


class ExamRepository:
    @staticmethod
    def __apply_interval_filter(
        *,
        statement: Select,
        interval: QueryInterval,
    ) -> Any:
        if interval.today:
            statement = (
                statement.join(
                    Reservation, col(Exam.reservation_id) == col(Reservation.id)
                )
                .join(Schedule, col(Schedule.reservation_id) == col(Reservation.id))
                .where(col(Schedule.end_date) >= interval.today)
            )

        if interval.start and interval.end:
            statement = (
                statement.join(
                    Reservation, col(Exam.reservation_id) == col(Reservation.id)
                )
                .join(Schedule, col(Schedule.reservation_id) == col(Reservation.id))
                .where(
                    col(Schedule.start_date) >= interval.start,
                    col(Schedule.end_date) <= interval.end,
                )
            )
        return statement

    @staticmethod
    def get_all(*, session: Session, interval: QueryInterval) -> list[Exam]:
        statement = select(Exam)
        statement = ExamRepository.__apply_interval_filter(
            statement=statement, interval=interval
        )
        return list(session.exec(statement).all())

    @staticmethod
    def get_all_by_subject_id(
        *, subject_id: int, session: Session, interval: QueryInterval
    ) -> list[Exam]:
        statement = select(Exam).where(Exam.subject_id == subject_id)
        statement = ExamRepository.__apply_interval_filter(
            statement=statement, interval=interval
        )
        exams = session.exec(statement).all()
        return list(exams)

    @staticmethod
    def get_all_by_class_id(
        *, class_id: int, session: Session, interval: QueryInterval
    ) -> list[Exam]:
        statement = (
            select(Exam)
            .join(ExamClassLink, col(ExamClassLink.exam_id) == col(Exam.id))
            .where(ExamClassLink.class_id == class_id)
        )
        statement = ExamRepository.__apply_interval_filter(
            statement=statement, interval=interval
        )
        exams = session.exec(statement).all()
        return list(exams)

    @staticmethod
    def get_by_id(*, id: int, session: Session) -> Exam:
        statement = select(Exam).where(Exam.id == id)
        exam = session.exec(statement).first()
        if exam is None:
            raise ExamNotFound()
        return exam

    @staticmethod
    def create(
        *, creator: User, input: ExamRegister, session: Session, allocate: bool = True
    ) -> Exam:
        classroom = ClassroomRepository.get_by_id(
            id=input.classroom_id, session=session
        )
        subject = SubjectRepository.get_by_id(id=input.subject_id, session=session)
        classes = ClassRepository.get_by_ids(ids=input.class_ids, session=session)

        for class_ in classes:
            if class_.subject_id != subject.id:
                raise ExamInvalidClassAndSubject()
        reservation = ReservationRepository.create(
            creator=creator,
            input=input,
            classroom=classroom,
            session=session,
            allocate=allocate,
        )
        exam = Exam(
            reservation=reservation,
            subject_id=must_be_int(subject.id),
            classes=classes,
        )  # pyright: ignore[reportCallIssue]
        session.add(exam)
        return exam

    @staticmethod
    def update(*, user: User, id: int, input: ExamUpdate, session: Session) -> Exam:
        exam = ExamRepository.get_by_id(id=id, session=session)
        classroom = ClassroomRepository.get_by_id(
            id=input.classroom_id, session=session
        )
        ReservationRepository.update(
            id=exam.reservation_id,
            input=input,
            classroom=classroom,
            user=user,
            session=session,
        )  # pyright: ignore[reportArgumentType]

        subject = SubjectRepository.get_by_id(id=input.subject_id, session=session)
        classes = ClassRepository.get_by_ids(ids=input.class_ids, session=session)

        for class_ in classes:
            if class_.subject_id != subject.id:
                raise ExamInvalidClassAndSubject()

        exam.subject_id = must_be_int(subject.id)
        exam.classes = classes
        session.add(exam)
        return exam


class ExamInvalidClassAndSubject(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Essa prova contém turmas com disciplinas inválidas",
        )


class ExamNotFound(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prova não encontrada",
        )
