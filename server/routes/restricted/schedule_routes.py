from fastapi import APIRouter

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.schedule_request_models import (
    ScheduleUpdateOccurrences,
)
from server.models.http.responses.schedule_response_models import ScheduleFullResponse
from server.repositories.schedule_repository import ScheduleRepository
from server.services.security.schedule_permission_checker import (
    schedule_permission_checker,
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
    schedule_permission_checker(user, schedule_id, session)
    schedule = ScheduleRepository.update_occurrences(
        id=schedule_id, input=input, session=session
    )
    session.commit()
    return ScheduleFullResponse.from_schedule(schedule)
