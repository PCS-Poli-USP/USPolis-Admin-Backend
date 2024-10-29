from fastapi import APIRouter
from server.routes.public.forum_routes import router as ForumRouter
from server.routes.public.mobile_classes_routes import router as MobileClassRouter
from server.routes.public.mobile_institutional_events_routes import (
    router as MobileInstitutionalEventsRouter,
)
from server.routes.public.mobile_comments_routes import router as MobileCommentsRouter
from server.routes.public.mobile_google_authentication_routes import (
    router as MobileGAuth,
)
from server.routes.public.mobile_programs_routes import router as ProgramsRouter
from server.routes.public.building_routes import router as BuildingRouter
from server.routes.public.class_routes import router as ClassRouter
from server.routes.public.classroom_routes import router as ClassroomRouter
from server.routes.public.reservation_routes import router as ReservationRouter
from server.routes.public.auth_route import router as AuthRouter


router = APIRouter()

router.include_router(ForumRouter)
router.include_router(MobileClassRouter)
router.include_router(MobileInstitutionalEventsRouter)
router.include_router(MobileCommentsRouter)
router.include_router(MobileGAuth)
router.include_router(ProgramsRouter)
router.include_router(BuildingRouter)
router.include_router(ClassRouter)
router.include_router(ClassroomRouter)
router.include_router(ReservationRouter)
router.include_router(AuthRouter)
