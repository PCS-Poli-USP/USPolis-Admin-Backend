from fastapi import APIRouter

from server.deps.session_dep import SessionDep
from server.models.http.responses.exam_response_models import ExamResponse
from server.repositories.exam_repository import ExamRepository


router = APIRouter(prefix="/exams", tags=["Exams"])


@router.get("")
def get_all_exams(session: SessionDep) -> list[ExamResponse]:
    exams = ExamRepository.get_all(session=session)
    return ExamResponse.from_exams(exams)
