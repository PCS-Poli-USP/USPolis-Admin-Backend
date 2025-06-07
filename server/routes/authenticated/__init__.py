from fastapi import APIRouter, Depends

from server.deps.authenticate import authenticate
from server.routes.authenticated.building_routes import router as BuildingRouter
from server.routes.authenticated.calendar_routes import router as CalendarRouter
from server.routes.authenticated.class_routes import router as ClassRouter
from server.routes.authenticated.reservation_routes import router as ReservationRouter
from server.routes.authenticated.classroom_routes import router as ClassroomRouter
from server.routes.authenticated.holiday_category_routes import (
    router as HolidayCateryRouter,
)
from server.routes.authenticated.holiday_routes import router as HolidayRouter
from server.routes.authenticated.institutional_event_routes import (
    router as InstitutionalEventRouter,
)
from server.routes.authenticated.subject_routes import router as SubjectRouter
from server.routes.authenticated.user_routes import router as UserRouter
from server.routes.authenticated.classroom_soliciation_routes import (
    router as ClassroomSolicitationRouter,
)


router = APIRouter(dependencies=[Depends(authenticate)], tags=["Authenticated"])

router.include_router(BuildingRouter)
router.include_router(ClassroomRouter)
router.include_router(SubjectRouter)
router.include_router(UserRouter)
router.include_router(HolidayCateryRouter)
router.include_router(HolidayRouter)
router.include_router(CalendarRouter)
router.include_router(InstitutionalEventRouter)
router.include_router(ClassRouter)
router.include_router(ReservationRouter)
router.include_router(ClassroomSolicitationRouter)
