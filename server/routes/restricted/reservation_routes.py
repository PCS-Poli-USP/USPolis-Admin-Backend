from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

from server.deps.repository_adapters.reservation_repository_adapter import (
    ReservationRepositoryDep,
)
from server.services.email.email_service import EmailService

from server.routes.restricted.exam_routes import router as ExamRouter
from server.routes.restricted.event_routes import router as EventRouter
from server.routes.restricted.meeting_routes import router as MeetingRouter

embed = Body(..., embed=True)

router = APIRouter(prefix="/reservations", tags=["Reservations"])
router.include_router(ExamRouter)
router.include_router(EventRouter)
router.include_router(MeetingRouter)


@router.delete("/{reservation_id}")
async def delete_reservation(
    reservation_id: int, repository: ReservationRepositoryDep
) -> JSONResponse:
    """Delete a Reservation by ID"""
    reservation = repository.get_by_id(id=reservation_id)
    repository.delete(id=reservation_id)
    if reservation.solicitation:
        await EmailService.send_solicitation_deleted_email(
            solicitation=reservation.solicitation,
        )
    return JSONResponse(content={"message": "Reserva removida com sucesso!"})
