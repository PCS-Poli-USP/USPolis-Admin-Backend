from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from server.deps.authenticate import UserDep
from server.deps.repository_adapters.meeting_repository_adapter import (
    MeetingRepositoryDep,
)
from server.models.http.requests.meeting_request_models import (
    MeetingRegister,
    MeetingUpdate,
)


router = APIRouter(prefix="/meetings", tags=["Reservations", "Meetings"])


@router.post("")
def create_meeting(
    input: MeetingRegister, user: UserDep, repository: MeetingRepositoryDep
) -> JSONResponse:
    repository.create(creator=user, input=input)
    return JSONResponse(
        content={"message": "Reunião criada com sucesso!"},
        status_code=status.HTTP_201_CREATED,
    )


@router.put("/{id}")
def update_meeting(
    id: int, input: MeetingUpdate, repository: MeetingRepositoryDep
) -> JSONResponse:
    repository.update(id=id, input=input)
    return JSONResponse(
        content={"message": "Reunião criada com sucesso!"},
        status_code=status.HTTP_201_CREATED,
    )
