from fastapi import APIRouter
from fastapi.responses import JSONResponse

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.exam_request_models import ExamRegister


router = APIRouter(prefix="/exams", tags=["Exams"])


@router.post("")
def create_exam(
    input: ExamRegister, creator: UserDep, session: SessionDep
) -> JSONResponse:
    return JSONResponse(content={"message": "Hello, World!"})
