from fastapi import APIRouter

from server.routes.dev.jupiter_debug_routes import router as JupiterDebugRouter

router = APIRouter()

router.include_router(JupiterDebugRouter)
