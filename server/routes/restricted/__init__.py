from fastapi import APIRouter, Depends

from server.deps.authenticate import restricted_authenticate
from server.routes.restricted.building_routes import router as BuildingRouter
from server.routes.restricted.calendar_routes import router as CalendarRouter
from server.routes.restricted.class_routes import router as ClassRouter
from server.routes.restricted.reservation_routes import router as ReservationRouter
from server.routes.restricted.classroom_routes import router as ClassroomRouter
from server.routes.restricted.conflict_routes import router as ConflictRouter
from server.routes.restricted.holiday_category_routes import (
    router as HolidayCateryRouter,
)
from server.routes.restricted.holiday_routes import router as HolidayRouter
from server.routes.restricted.institutional_event_routes import (
    router as InstitutionalEventRouter,
)
from server.routes.restricted.schedule_routes import router as ScheduleRouter
from server.routes.restricted.occurrence_routes import router as OccurrenceRouter
from server.routes.restricted.subject_routes import router as SubjectRouter
from server.routes.restricted.solicitation_routes import (
    router as SolicitationRouter,
)
from server.routes.restricted.allocation_routes import (
    router as AllocationRouter,
)
from server.routes.restricted.allocation_log_routes import (
    router as AllocationLogRouter,
)

router = APIRouter(dependencies=[Depends(restricted_authenticate)], tags=["Restricted"])

router.include_router(BuildingRouter)
router.include_router(ClassroomRouter)
router.include_router(SubjectRouter)
router.include_router(HolidayCateryRouter)
router.include_router(HolidayRouter)
router.include_router(CalendarRouter)
router.include_router(InstitutionalEventRouter)
router.include_router(ClassRouter)
router.include_router(ReservationRouter)
router.include_router(ScheduleRouter)
router.include_router(OccurrenceRouter)
router.include_router(ConflictRouter)
router.include_router(SolicitationRouter)
router.include_router(AllocationRouter)
router.include_router(AllocationLogRouter)
