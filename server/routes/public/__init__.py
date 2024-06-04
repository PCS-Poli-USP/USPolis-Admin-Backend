from fastapi import APIRouter, Depends

from server.deps.authenticate import authenticate
from server.routes.public.building_routes import router as BuildingRouter
from server.routes.public.classroom_routes import router as ClassroomRouter
from server.routes.public.holiday_category_routes import router as HolidayCateryRouter
from server.routes.public.holiday_routes import router as HolidayRouter
from server.routes.public.calendar_routes import router as CalendarRouter
from server.routes.public.subject_routes import router as SubjectRouter
from server.routes.public.user_routes import router as UserRouter
from server.routes.public.department_routes import router as DepartmentRouter

router = APIRouter(dependencies=[Depends(authenticate)])

router.include_router(BuildingRouter)
router.include_router(ClassroomRouter)
router.include_router(SubjectRouter)
router.include_router(UserRouter)
router.include_router(HolidayCateryRouter)
router.include_router(HolidayRouter)
router.include_router(CalendarRouter)
router.include_router(DepartmentRouter)
