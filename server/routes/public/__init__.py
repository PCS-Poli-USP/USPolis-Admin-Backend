from fastapi import APIRouter
from server.routes.public.mobile_classes_routes import router as MobileClassRouter
from server.routes.public.mobile_institutional_events_routes import router as MobileInstitutionalEventsRouter

router = APIRouter()

router.include_router(MobileClassRouter)
router.include_router(MobileInstitutionalEventsRouter)