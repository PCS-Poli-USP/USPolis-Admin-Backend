from fastapi import APIRouter, Body, Response

from server.deps.repository_adapters.reservation_repository_adapter import (
    ReservationRepositoryDep,
)
from server.models.http.requests.classroom_solicitation_request_models import (
    ClassroomSolicitationApprove,
    ClassroomSolicitationUpdated,
)
from server.models.http.requests.reservation_request_models import (
    ReservationRegister,
    ReservationUpdate,
)
from server.models.http.responses.generic_responses import NoContent
from server.models.http.responses.reservation_response_models import (
    ReservationResponse,
)
from server.services.email.email_service import EmailService

embed = Body(..., embed=True)

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.get("/{reservation_id}")
def get_reservation(
    reservation_id: int, repository: ReservationRepositoryDep
) -> ReservationResponse:
    """Get an reservation by id"""
    reservation = repository.get_by_id(id=reservation_id)
    return ReservationResponse.from_reservation(reservation)


@router.post("")
async def create_reservation(
    input: ReservationRegister, repository: ReservationRepositoryDep
) -> ReservationResponse:
    """Create a reservation"""
    reservation = repository.create(reservation=input)
    if (
        reservation.solicitation
        and input.solicitation_id
        and input.solicitation_id == reservation.solicitation.id
    ):
        solicitation_approve = ClassroomSolicitationApprove(
            classroom_id=reservation.classroom_id,
            classroom_name=reservation.classroom.name,
            start_time=reservation.schedule.start_time,
            end_time=reservation.schedule.end_time,
        )
        await EmailService.send_solicitation_approved_email(
            input=solicitation_approve, solicitation=reservation.solicitation
        )
    return ReservationResponse.from_reservation(reservation)


@router.put("/{reservation_id}")
async def update_reservation(
    reservation_id: int, input: ReservationUpdate, repository: ReservationRepositoryDep
) -> ReservationResponse:
    """Update a reservation by ID"""
    old_reservation = repository.get_by_id(id=reservation_id)
    reservation = repository.update(id=reservation_id, input=input)
    if input.has_solicitation and input.solicitation_id:
        if old_reservation.solicitation and reservation.solicitation:
            solicitation_input = ClassroomSolicitationUpdated(
                classroom_id=reservation.classroom_id,
                classroom_name=reservation.classroom.name,
                start_time=reservation.schedule.start_time,
                end_time=reservation.schedule.end_time,
            )
            await EmailService.send_solicitation_updated_email(
                input=solicitation_input, solicitation=reservation.solicitation
            )
        else:
            if reservation.solicitation and not old_reservation.solicitation:
                solicitation_approve = ClassroomSolicitationApprove(
                    classroom_id=reservation.classroom_id,
                    classroom_name=reservation.classroom.name,
                    start_time=reservation.schedule.start_time,
                    end_time=reservation.schedule.end_time,
                )
                await EmailService.send_solicitation_approved_email(
                    input=solicitation_approve, solicitation=reservation.solicitation
                )
    return ReservationResponse.from_reservation(reservation)


@router.delete("/{reservation_id}")
async def delete_reservation(
    reservation_id: int, repository: ReservationRepositoryDep
) -> Response:
    """Delete a Reservation by ID"""
    reservation = repository.get_by_id(id=reservation_id)
    if reservation.solicitation:
        await EmailService.send_solicitation_deleted_email(
            reservation=reservation,
            solicitation=reservation.solicitation,
        )
    repository.delete(id=reservation_id)
    return NoContent
