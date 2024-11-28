from fastapi import APIRouter, Body

from server.models.http.responses.subject_response_models import SubjectResponse

from server.deps.session_dep import SessionDep
from server.repositories.subject_repository import SubjectRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/subjects", tags=["Subjects", "Public"])


@router.get("")
async def get_all_subjects(session: SessionDep) -> list[SubjectResponse]:
    """Get all subjects"""
    subjects = SubjectRepository.get_all(session=session)
    return SubjectResponse.from_subject_list(subjects)
