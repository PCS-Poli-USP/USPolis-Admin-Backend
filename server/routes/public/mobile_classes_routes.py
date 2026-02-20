from fastapi import APIRouter

from server.cache import simple_cache
from server.deps.interval_dep import QueryIntervalDep
from server.deps.session_dep import SessionDep
from server.models.database.class_db_model import Class
from server.repositories.class_repository import ClassRepository
from server.models.http.responses.mobile_class_response_models import (
    MobileClassResponse,
)

router = APIRouter(prefix="/mobile/classes", tags=["Mobile", "Classes"])


@router.get("")
@simple_cache(expire_seconds=60)
async def get_all_classes(
    session: SessionDep, interval: QueryIntervalDep
) -> list[MobileClassResponse]:
    """Get all classes, converted for mobile use"""
    classes: list[Class] = ClassRepository.get_all(session=session, interval=interval)
    return MobileClassResponse.from_model_list(classes, interval=interval)
