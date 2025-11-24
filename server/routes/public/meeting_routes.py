from fastapi import APIRouter

from server.deps.interval_dep import QueryIntervalDep
from server.deps.session_dep import SessionDep
from server.models.http.responses.meeting_response_models import MeetingResponse
from server.repositories.meeting_repository import MeetingRepository


router = APIRouter(prefix="/meetings", tags=["Reservations", "Meetings"])


@router.get("")
def get_all_meetings(
    session: SessionDep, interval: QueryIntervalDep
) -> list[MeetingResponse]:
    meetings = MeetingRepository.get_all(session=session, interval=interval)
    return MeetingResponse.from_meetings(meetings)
