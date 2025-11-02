from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from server.deps.authenticate import UserDep
from server.deps.repository_adapters.exam_repository_adapter import ExamRepositoryDep
from server.models.http.requests.exam_request_models import ExamRegister, ExamUpdate


router = APIRouter(prefix="/exams", tags=["Reservations", "Exams"])


@router.post("")
def create_exam(
    input: ExamRegister, creator: UserDep, repository: ExamRepositoryDep
) -> JSONResponse:
    repository.create(creator=creator, input=input)
    return JSONResponse(
        content={"message": "Prova criada com sucesso!"},
        status_code=status.HTTP_201_CREATED,
    )


@router.put("/{id}")
def update_exam(
    id: int, input: ExamUpdate, repository: ExamRepositoryDep
) -> JSONResponse:
    repository.update(id=id, input=input)
    return JSONResponse(
        content={"message": "Prova atualizada com sucesso!"},
        status_code=status.HTTP_200_OK,
    )
