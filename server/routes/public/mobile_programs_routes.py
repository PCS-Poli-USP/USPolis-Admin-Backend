from fastapi import APIRouter

from server.deps.session_dep import SessionDep

router = APIRouter(prefix="/mobile/programs", tags=["Mobile", "Programs"])


@router.get("")
async def get_all_programs(session: SessionDep) -> list:
    """Get all programs (?)"""
    return []
