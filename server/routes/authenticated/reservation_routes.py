from fastapi import APIRouter, Body

from server.deps.repository_adapters.reservation_repository_adapter import (
    ReservationRepositoryDep,
)
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
