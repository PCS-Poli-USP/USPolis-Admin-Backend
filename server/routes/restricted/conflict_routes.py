from datetime import date
from fastapi import APIRouter

from server.deps.conflict_checker import ConflictCheckerDep
from server.services.conflict_checker import BuildingConflictSpecification
from server.utils.enums.confict_enum import ConflictType

router = APIRouter(prefix="/conflicts", tags=["Conflicts"])


@router.get("")
def get_conflicts(
    type: ConflictType,
    conflict_checker: ConflictCheckerDep,
    start: date = date.today().replace(month=7, day=1)
    if date.today().month > 6
    else date.today().replace(month=1, day=1),
    end: date = date.today().replace(month=12, day=31)
    if date.today().month > 6
    else date.today().replace(month=6, day=30),
) -> list[BuildingConflictSpecification]:
    conflicts = conflict_checker.specificate_conflicts_for_allowed_classrooms(
        start=start, end=end, type=type
    )
    return conflicts
