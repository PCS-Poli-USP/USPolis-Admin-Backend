from fastapi import APIRouter

from server.deps.conflict_checker import ConflictCheckerDep
from server.services.conflict_checker import BuildingConflictSpecification

router = APIRouter(prefix="/conflicts", tags=["Conflicts"])


@router.get("")
def get_conflicts(
    conflict_checker: ConflictCheckerDep,
) -> list[BuildingConflictSpecification]:
    conflicts = conflict_checker.conflicts_for_allowed_classrooms()
    return conflicts
