from fastapi import APIRouter, Depends

from server.deps.authenticate import authenticate
from server.routes.restricted.building_routes import router as BuildingRouter
from server.routes.restricted.calendar_routes import router as CalendarRouter
from server.routes.restricted.class_routes import router as ClassRouter
from server.routes.restricted.classroom_routes import router as ClassroomRouter
from server.routes.restricted.holiday_category_routes import (
    router as HolidayCateryRouter,
)
from server.routes.restricted.holiday_routes import router as HolidayRouter
from server.routes.restricted.institutional_event_routes import (
    router as InstitutionalEventRouter,
)
from server.routes.restricted.occurrence_routes import router as OccurrenceRouter
from server.routes.restricted.subject_routes import router as SubjectRouter
from server.routes.restricted.user_routes import router as UserRouter

router = APIRouter(dependencies=[Depends(authenticate)])

router.include_router(BuildingRouter)
router.include_router(ClassroomRouter)
router.include_router(SubjectRouter)
router.include_router(UserRouter)
router.include_router(HolidayCateryRouter)
router.include_router(HolidayRouter)
router.include_router(CalendarRouter)
router.include_router(InstitutionalEventRouter)
router.include_router(ClassRouter)
router.include_router(OccurrenceRouter)
