from server.app import app
from server.routes.test_routes import router as TestRouter
from server.routes.user_routes import router as UserRouter

app.include_router(UserRouter)
app.include_router(TestRouter)