from fastapi import APIRouter
from fastapi.params import Depends

from server.deps.authenticate import building_authenticate

router = APIRouter(
    prefix="/schedules/{building_id}/",
    tags=["Classrooms"],
    dependencies=[Depends(building_authenticate)],
)