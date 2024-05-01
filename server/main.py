"""Server main runtime."""

from server.app import app
from server.routes.user import router as UserRouter

app.include_router(UserRouter)
