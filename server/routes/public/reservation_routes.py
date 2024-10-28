from fastapi import APIRouter, Body

from server.deps.session_dep import SessionDep
from server.models.http.responses.reservation_response_models import (
    ReservationResponse,
    ReservationFullResponse,
)
from server.repositories.reservation_repository import ReservationRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/reservations", tags=["Public", "Reservations"])


@router.get("")
async def get_all_reservations(
    session: SessionDep,
) -> list[ReservationResponse]:
    """Get all reservations on user buildings"""
    reservations = ReservationRepository.get_all(session=session)
    return ReservationResponse.from_reservation_list(reservations)


@router.get("/full/")
async def get_all_reservations_full(
    session: SessionDep,
) -> list[ReservationFullResponse]:
    """Get all reservations with occurrences on user buildings"""
    reservations = ReservationRepository.get_all(session=session)
    return ReservationFullResponse.from_reservation_list(reservations)
