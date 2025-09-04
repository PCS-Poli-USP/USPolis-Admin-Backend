from fastapi import APIRouter

from server.deps.session_dep import SessionDep
from server.models.http.responses.exam_response_models import (
    ExamEventResponse,
    ExamResponse,
)
from server.repositories.exam_repository import ExamRepository


router = APIRouter(prefix="/exams", tags=["Reservations", "Exams"])


@router.get("")
def get_all_exams(session: SessionDep) -> list[ExamResponse]:
    exams = ExamRepository.get_all(session=session)
    return ExamResponse.from_exams(exams)


@router.get("/events")
def get_all_exam_events(session: SessionDep) -> list[ExamEventResponse]:
    exams = ExamRepository.get_all(session=session)
    return ExamEventResponse.from_exams(exams)


@router.get("/subjects/{subject_id}")
def get_all_subject_exams(subject_id: int, session: SessionDep) -> list[ExamResponse]:
    exams = ExamRepository.get_all_by_subject_id(subject_id=subject_id, session=session)
    return ExamResponse.from_exams(exams)


@router.get("/classes/{class_id}")
def get_all_class_exams(class_id: int, session: SessionDep) -> list[ExamResponse]:
    exams = ExamRepository.get_all_by_class_id(class_id=class_id, session=session)
    return ExamResponse.from_exams(exams)
