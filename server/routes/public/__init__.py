from fastapi import APIRouter, Depends

from server.routes.public.building_routes import router as BuildingRouter
from server.routes.public.classroom_routes import router as ClassroomRouter
from server.routes.public.subject_routes import router as SubjectRouter
from server.routes.public.user_routes import router as UserRouter
from server.services.auth.authenticate import authenticate

router = APIRouter(dependencies=[Depends(authenticate)])

router.include_router(BuildingRouter)
router.include_router(ClassroomRouter)
router.include_router(SubjectRouter)
router.include_router(UserRouter)
