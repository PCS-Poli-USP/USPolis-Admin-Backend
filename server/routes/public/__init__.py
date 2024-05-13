from fastapi import APIRouter, Depends

from server.routes.public.classroom_routes import router as ClassroomRouter
from server.routes.public.subject_routes import router as SubjectRouter
from server.services.auth.authenticate import authenticate

router = APIRouter(dependencies=[Depends(authenticate)])

router.include_router(SubjectRouter)
router.include_router(ClassroomRouter)
