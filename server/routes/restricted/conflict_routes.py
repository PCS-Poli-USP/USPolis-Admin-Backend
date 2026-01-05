from datetime import date
from fastapi import APIRouter

from server.deps.conflict_checker import ConflictCheckerDep
from server.services.conflict_checker import BuildingConflictSpecification
from server.utils.enums.confict_enum import ConflictType

router = APIRouter(prefix="/conflicts", tags=["Conflicts"])


@router.get("/building/{building_id}")
def get_conflicts(
    building_id: int,
    type: ConflictType,
    conflict_checker: ConflictCheckerDep,
    start: date | None = None,
    end: date | None = None,
) -> BuildingConflictSpecification:
    conflicts = (
        conflict_checker.specificate_conflicts_for_allowed_classrooms_in_building(
            building_id=building_id, type=type, start=start, end=end
        )
    )
    return conflicts
