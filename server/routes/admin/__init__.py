from fastapi import APIRouter, Depends

from server.deps.authenticate import admin_authenticate, admin_authenticate_from_cookie
from server.routes.admin.building_admin_routes import router as AdminBuildingRouter
from server.routes.admin.user_admin_routes import router as AdminUserRouter
from server.routes.admin.mobile_admin_routes import router as AdminMobileRouter
from server.routes.admin.group_admin_routes import router as AdminGroupRouter
from server.routes.admin.feedback_admin_routes import router as AdminFeedbackRouter
from server.routes.admin.bug_report_admin_routes import router as AdminBugReportRouter
from server.routes.admin.bug_report_evidence_admin_routes import (
    cookie_router as AdminBugReportEvidenceCookieRouter,
    router as AdminBugReportEvidenceRouter,
)

router = APIRouter(
    prefix="/admin", tags=["Admin"], dependencies=[Depends(admin_authenticate)]
)

router.include_router(AdminUserRouter)
router.include_router(AdminBuildingRouter)
router.include_router(AdminMobileRouter)
router.include_router(AdminGroupRouter)
router.include_router(AdminFeedbackRouter)
router.include_router(AdminBugReportRouter)
router.include_router(AdminBugReportEvidenceRouter)

cookie_router = APIRouter(
    prefix="/images/admin",
    tags=["Admin", "Cookie"],
    dependencies=[Depends(admin_authenticate_from_cookie)],
)

cookie_router.include_router(AdminBugReportEvidenceCookieRouter)
