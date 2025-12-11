from fastapi import APIRouter, Body

from server.deps.interval_dep import QueryIntervalDep
from server.deps.session_dep import SessionDep
from server.models.http.responses.reservation_response_models import (
    ReservationResponse,
    ReservationFullResponse,
)
from server.repositories.building_repository import BuildingRepository
from server.repositories.reservation_repository import ReservationRepository
from server.utils.must_be_int import must_be_int

from server.routes.public.exam_routes import router as ExamRouter
from server.routes.public.event_routes import router as EventRouter
from server.routes.public.meeting_routes import router as MeetingRouter


embed = Body(..., embed=True)

router = APIRouter(prefix="/reservations", tags=["Reservations"])

router.include_router(ExamRouter)
router.include_router(EventRouter)
router.include_router(MeetingRouter)


@router.get("")
async def get_all_reservations(
    session: SessionDep, interval: QueryIntervalDep
) -> list[ReservationResponse]:
    """Get all reservations"""
    reservations = ReservationRepository.get_all(session=session, interval=interval)
    return ReservationResponse.from_reservation_list(reservations)


@router.get("/full/")
async def get_all_reservations_full(
    session: SessionDep, interval: QueryIntervalDep
) -> list[ReservationFullResponse]:
    """Get all reservations with occurrences on user buildings"""
    reservations = ReservationRepository.get_all(session=session, interval=interval)
    return ReservationFullResponse.from_reservation_list(reservations)


@router.get("/building/{building_name}")
async def get_all_reservations_by_building_name(
    building_name: str, session: SessionDep, interval: QueryIntervalDep
) -> list[ReservationResponse]:
    """Get all classes by building name"""
    building = BuildingRepository.get_by_name(name=building_name, session=session)
    reservations = ReservationRepository.get_all_on_buildings(
        building_ids=[must_be_int(building.id)], session=session, interval=interval
    )
    return ReservationResponse.from_reservation_list(reservations)
