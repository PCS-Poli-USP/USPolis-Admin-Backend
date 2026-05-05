from fastapi import APIRouter, Body

from server.deps.session_dep import SessionDep
from server.models.http.responses.curriculum_response_models import CurriculumResponse
from server.repositories.curriculum_repository import CurriculumRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/curriculums", tags=["Curriculums"])

@router.get("")
async def get_all_curriculums(session: SessionDep) -> list[CurriculumResponse]:
    """Get all curriculums"""
    curriculums = CurriculumRepository.get_all(session=session)
    return CurriculumResponse.from_curriculum_list(curriculums)
