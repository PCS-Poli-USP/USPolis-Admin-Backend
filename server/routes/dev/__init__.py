from fastapi import APIRouter, Depends

from server.deps.authenticate import admin_authenticate
from server.routes.dev.jupiter_debug_routes import router as JupiterDebugRouter

router = APIRouter(dependencies=[Depends(admin_authenticate)])

router.include_router(JupiterDebugRouter)
