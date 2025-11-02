from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from server.deps.authenticate import UserDep
from server.deps.repository_adapters.event_repository_adapter import EventRepositoryDep
from server.models.http.requests.event_request_models import EventRegister, EventUpdate


router = APIRouter(prefix="/events", tags=["Reservations", "Events"])


@router.post("")
def create_event(
    input: EventRegister, user: UserDep, repository: EventRepositoryDep
) -> JSONResponse:
    repository.create(creator=user, input=input)
    return JSONResponse(
        content={"message": "Evento criado com sucesso!"},
        status_code=status.HTTP_201_CREATED,
    )


@router.put("/{id}")
def update_event(
    id: int, input: EventUpdate, repository: EventRepositoryDep
) -> JSONResponse:
    repository.update(id=id, input=input)
    return JSONResponse(
        content={"message": "Evento atualizado com sucesso!"},
        status_code=status.HTTP_200_OK,
    )
