from fastapi import APIRouter, Depends

from server.deps.authenticate import admin_authenticate
from server.routes.admin.building_admin_routes import router as AdminBuildingRouter
from server.routes.admin.user_admin_routes import router as AdminUserRouter
from server.routes.admin.mobile_admin_routes import router as AdminMobileRouter
from server.routes.admin.group_admin_routes import router as AdminGroupRouter
from server.routes.admin.feedback_admin_routes import router as AdminFeedbackRouter
from server.routes.admin.bug_report_admin_routes import router as AdminBugReportRouter
from server.routes.admin.bug_report_evidence_admin_routes import (
    router as AdminBugReportEvidenceRouter,
)
from server.routes.admin.user_session_admin_routes import (
    router as AdminUserSessionRouter,
)
from server.routes.admin.course_admin_routes import router as AdminCourseRouter
from server.routes.admin.curriculum_admin_routes import router as AdminCurriculumRouter
from server.routes.admin.curriculum_subject_admin_routes import (
    router as AdminCurriculumSubjectRouter,
)
from server.routes.admin.api_access_log_admin_routes import (
    router as AdminApiAccessLogRouter,
)
from server.routes.admin.api_incident_report_admin_routes import (
    router as AdminApiIncidentReportRouter,
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
router.include_router(AdminUserSessionRouter)
router.include_router(AdminCourseRouter)
router.include_router(AdminCurriculumRouter)
router.include_router(AdminCurriculumSubjectRouter)
router.include_router(AdminApiAccessLogRouter)
router.include_router(AdminApiIncidentReportRouter)
