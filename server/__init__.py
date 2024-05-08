from server.app import app
from server.routes.test_routes import router as TestRouter
from server.routes.user_routes import router as UserRouter
from server.routes.building_routes import router as BuildingRouter
from server.routes.subject_routes import router as SubjecRouter
from server.routes.classroom_routes import router as ClassroomRouter
from server.routes.holiday_category_routes import router as HolidayCatergoryRouter


app.include_router(TestRouter)
app.include_router(UserRouter)
app.include_router(BuildingRouter)
app.include_router(SubjecRouter)
app.include_router(ClassroomRouter)
app.include_router(HolidayCatergoryRouter)
