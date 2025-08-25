from fastapi import HTTPException, status
from sqlmodel import Session
from server.models.database.exam_db_model import Exam
from server.models.database.user_db_model import User
from server.models.http.requests.exam_request_models import ExamRegister
from server.repositories.class_repository import ClassRepository
from server.repositories.classroom_repository import ClassroomRepository
from server.repositories.reservation_repository import ReservationRepository
from server.repositories.subject_repository import SubjectRepository
from server.utils.must_be_int import must_be_int


class ExamRepository:
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
            reservation_id=reservation.id,  # type: ignore
            reservation=reservation,
            subject_id=must_be_int(subject.id),
            classes=classes,
        )
        session.add(exam)
        return exam


class ExamInvalidClassAndSubject(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Essa prova contém turmas com disciplinas inválidas",
        )
