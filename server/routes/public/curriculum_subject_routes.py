from fastapi import APIRouter, Body, HTTPException

from server.deps.session_dep import SessionDep
from server.models.http.responses.curriculum_subject_response_models import CurriculumSubjectResponse
from server.repositories.curriculum_subject_repository import CurriculumSubjectRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/curriculum_subjects", tags=["CurriculumSubjects"])

@router.get("/{curriculum_id}/subjects")
async def get_subjects_by_curriculum(curriculum_id: int, session: SessionDep
    ) -> list[CurriculumSubjectResponse]:
    """Get all subjects by curriculum"""
    curriculum_subjects = CurriculumSubjectRepository.get_by_curriculum_id(curriculum_id=curriculum_id, session=session)
    if not curriculum_subjects:
        raise HTTPException(
            status_code=404,
            detail="Disciplinas do currículo não encontradas"
        )
    return CurriculumSubjectResponse.from_curriculum_subject_list(curriculum_subjects)
