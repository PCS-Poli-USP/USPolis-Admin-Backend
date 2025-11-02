from fastapi import APIRouter
from fastapi.responses import JSONResponse

from server.deps.authenticate import UserDep
from server.deps.repository_adapters.schedule_repository_adapter import (
    ScheduleRepositoryDep,
)
from server.deps.session_dep import SessionDep
from server.models.http.requests.schedule_request_models import (
    ScheduleManyRegister,
    ScheduleRegister,
    ScheduleUpdateOccurrences,
)
from server.models.http.responses.schedule_response_models import (
    ScheduleFullResponse,
    ScheduleResponse,
)
from server.repositories.schedule_repository import ScheduleRepository
from server.services.security.schedule_permission_checker import (
    SchedulePermissionChecker,
)

router = APIRouter(
    prefix="/schedules",
    tags=["Schedules"],
)


@router.patch("/{schedule_id}/edit-occurrences")
def update_occurentes(
    schedule_id: int,
    input: ScheduleUpdateOccurrences,
    user: UserDep,
    session: SessionDep,
) -> ScheduleFullResponse:
    checker = SchedulePermissionChecker(user=user, session=session)
    checker.check_permission(schedule_id)
    schedule = ScheduleRepository.update_occurrences(
        id=schedule_id, input=input, session=session
    )
    session.commit()
    return ScheduleFullResponse.from_schedule(schedule)


@router.post("/create-for-class/{class_id}")
def create_schedule_for_class(
    class_id: int, input: ScheduleRegister, repository: ScheduleRepositoryDep
) -> ScheduleResponse:
    schedule = repository.create_with_class(class_id=class_id, input=input)
    return ScheduleResponse.from_schedule(schedule)


@router.post("/create-many-for-classes")
def create_many_schedule_for_classes(
    data: ScheduleManyRegister, repository: ScheduleRepositoryDep
) -> JSONResponse:
    repository.create_many_with_class(inputs=data.inputs)
    return JSONResponse(
        content={
            "message": "Agendas criadas com sucesso",
        },
        status_code=201,
    )
