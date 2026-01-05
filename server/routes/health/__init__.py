from fastapi import APIRouter
from server.routes.health.health_routes import router as HealthRouter

router = APIRouter()

router.include_router(HealthRouter)
