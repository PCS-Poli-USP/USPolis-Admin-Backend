from fastapi import APIRouter, Body, Response

from server.deps.repository_adapters.reservation_repository_adapter import (
    ReservationRepositoryDep,
)
from server.models.http.requests.reservation_request_models import (
    ReservationRegister,
    ReservationUpdate,
)
from server.models.http.responses.generic_responses import NoContent
from server.models.http.responses.reservation_response_models import (
    ReservationResponse,
)

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
def create_reservation(
    input: ReservationRegister, repository: ReservationRepositoryDep
) -> ReservationResponse:
    """Create a reservation"""
    reservation = repository.create(reservation=input)
    return ReservationResponse.from_reservation(reservation)


@router.put("/{reservation_id}")
def update_reservation(
    reservation_id: int, input: ReservationUpdate, repository: ReservationRepositoryDep
) -> ReservationResponse:
    """Update a reservation by ID"""
    reservation = repository.update(id=reservation_id, input=input)
    return ReservationResponse.from_reservation(reservation)


@router.delete("/{reservation_id}")
def delete_reservation(
    reservation_id: int, repository: ReservationRepositoryDep
) -> Response:
    """Delete a Reservation by ID"""
    repository.delete(id=reservation_id)
    return NoContent
