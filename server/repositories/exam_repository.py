from fastapi import HTTPException, status
from sqlmodel import Session, select
from server.models.database.exam_db_model import Exam
from server.models.database.user_db_model import User
from server.models.http.requests.exam_request_models import ExamRegister, ExamUpdate
from server.repositories.class_repository import ClassRepository
from server.repositories.classroom_repository import ClassroomRepository
from server.repositories.reservation_repository import ReservationRepository
from server.repositories.subject_repository import SubjectRepository
from server.utils.must_be_int import must_be_int


class ExamRepository:
    @staticmethod
    def get_all(*, session: Session) -> list[Exam]:
        statement = select(Exam)
        return list(session.exec(statement).all())

    @staticmethod
    def get_all_by_subject_id(*, subject_id: int, session: Session) -> list[Exam]:
        subject = SubjectRepository.get_by_id(id=subject_id, session=session)
        return subject.exams

    @staticmethod
    def get_all_by_class_id(*, class_id: int, session: Session) -> list[Exam]:
        class_ = ClassRepository.get_by_id(id=class_id, session=session)
        return class_.exams

    @staticmethod
    def get_by_id(*, id: int, session: Session) -> Exam:
        statement = select(Exam).where(Exam.id == id)
        exam = session.exec(statement).first()
        if exam is None:
            raise ExamNotFound()
        return exam

    @staticmethod
    def create(*, creator: User, input: ExamRegister, session: Session) -> Exam:
        classroom = ClassroomRepository.get_by_id(
            id=input.classroom_id, session=session
        )
        subject = SubjectRepository.get_by_id(id=input.subject_id, session=session)
        classes = ClassRepository.get_by_ids(ids=input.class_ids, session=session)

        for class_ in classes:
            if class_.subject_id != subject.id:
                raise ExamInvalidClassAndSubject()
        reservation = ReservationRepository.create(
            creator=creator, input=input, classroom=classroom, session=session
        )
        exam = Exam(
            reservation=reservation,
            subject_id=must_be_int(subject.id),
            classes=classes,
        ) # pyright: ignore[reportCallIssue]
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

    @staticmethod
    def delete(*, id: int, user: User, session: Session) -> None:
        exam = ExamRepository.get_by_id(id=id, session=session)
        solicitation = exam.get_solicitation()
        if solicitation:
            ReservationRepository.delete(
                id=exam.reservation_id, user=user, session=session
            )
        if not solicitation:
            session.delete(exam)


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
