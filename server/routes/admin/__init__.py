from fastapi import APIRouter, Depends

from server.deps.authenticate import admin_authenticate
from server.routes.admin.building_admin_routes import router as AdminBuildingRouter
from server.routes.admin.user_admin_routes import router as AdminUserRouter
from server.routes.admin.mobile_admin_routes import router as AdminMobileRouter

router = APIRouter(
    prefix="/admin", tags=["Admin"], dependencies=[Depends(admin_authenticate)]
)

router.include_router(AdminUserRouter)
router.include_router(AdminBuildingRouter)
router.include_router(AdminMobileRouter)
