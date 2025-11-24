from fastapi import APIRouter, Body

from server.deps.interval_dep import QueryIntervalDep
from server.models.http.responses.subject_response_models import SubjectResponse

from server.deps.session_dep import SessionDep
from server.repositories.subject_repository import SubjectRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.get("")
async def get_all_subjects(session: SessionDep) -> list[SubjectResponse]:
    """Get all subjects"""
    subjects = SubjectRepository.get_all(session=session)
    return SubjectResponse.from_subject_list(subjects)


@router.get("/actives")
async def get_all_subjects_active(
    session: SessionDep, interval: QueryIntervalDep
) -> list[SubjectResponse]:
    """Get all subjects that have classes on interval"""
    subjects = SubjectRepository.get_all_on_interval(interval=interval, session=session)
    return SubjectResponse.from_subject_list(subjects)
