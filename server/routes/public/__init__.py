from fastapi import APIRouter
from server.routes.public.forum_routes import router as ForumRouter

router = APIRouter()

# router.include_router(YourRouter)

router.include_router(ForumRouter)