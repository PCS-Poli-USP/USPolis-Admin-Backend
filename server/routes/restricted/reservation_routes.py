import asyncio
from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

from server.deps.authenticate import UserDep
from server.deps.permission_index_dep import PermissionIndexDep
from server.deps.repository_adapters.reservation_repository_adapter import (
    ReservationRepositoryDep,
)
from server.deps.session_dep import SessionDep
from server.models.http.requests.schedule_request_models import (
    ScheduleUpdateOccurrences,
)
from server.models.http.responses.reservation_response_models import (
    ReservationFullResponse,
    ReservationResponse,
)
from server.services.email.email_service import EmailService
from server.services.security.reservation_permission_checker import (
    ReservationPermissionChecker,
)
from server.repositories.reservation_repository import ReservationRepository
from server.utils.enums.actions_enums import ClassroomAction

from server.routes.restricted.exam_routes import router as ExamRouter
from server.routes.restricted.event_routes import router as EventRouter
from server.routes.restricted.meeting_routes import router as MeetingRouter

embed = Body(..., embed=True)

router = APIRouter(prefix="/reservations", tags=["Reservations"])

router.include_router(ExamRouter)
router.include_router(EventRouter)
router.include_router(MeetingRouter)

@router.get("/{reservation_id}/full", response_model=ReservationFullResponse)
def get_reservation_full(
    reservation_id: int,
    repository: ReservationRepositoryDep,
) -> ReservationFullResponse:
    reservation = repository.get_by_id(id=reservation_id)
    return ReservationFullResponse.from_reservation(reservation)

@router.get("/{reservation_id}", response_model=ReservationResponse)
def get_reservation(
    reservation_id: int,
    repository: ReservationRepositoryDep,
) -> ReservationResponse:
    reservation = repository.get_by_id(id=reservation_id)
    return ReservationResponse.from_reservation(reservation)

@router.patch("/{reservation_id}/edit-occurrences")
def update_reservation_occurrences(
    reservation_id: int,
    input: ScheduleUpdateOccurrences,
    user: UserDep,
    session: SessionDep,
    permission_index: PermissionIndexDep,
) -> ReservationFullResponse:
    checker = ReservationPermissionChecker(
        user=user, session=session, permission_index=permission_index
    )
    checker.check_permission(reservation_id, ClassroomAction.RESERVE)
    reservation = ReservationRepository.update_occurrences(
        id=reservation_id, input=input, session=session
    )
    session.commit()
    return ReservationFullResponse.from_reservation(reservation)

@router.delete("/{reservation_id}")
async def delete_reservation(
    reservation_id: int, repository: ReservationRepositoryDep
) -> JSONResponse:
    """Delete a Reservation by ID"""
    reservation = repository.get_by_id(id=reservation_id)
    repository.delete(id=reservation_id)

    if reservation.solicitation:
        asyncio.create_task(
            EmailService.send_solicitation_deleted_email(
                solicitation=reservation.solicitation,
            )
        )
    return JSONResponse(content={"message": "Reserva removida com sucesso!"})
