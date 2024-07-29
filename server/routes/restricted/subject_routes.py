from fastapi import APIRouter, Body, Response

from server.deps.authenticate import BuildingDep
from server.deps.repository_adapters.subject_repository_adapter import (
    SubjectRepositoryDep,
)
from server.deps.session_dep import SessionDep
from server.models.database.subject_db_model import Subject
from server.models.http.requests.subject_request_models import (
    SubjectRegister,
    SubjectUpdate,
)
from server.models.http.responses.generic_responses import NoContent
from server.models.http.responses.subject_response_models import SubjectResponse
from server.repositories.subject_repository import SubjectRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.get("")
async def get_all_subjects(repository: SubjectRepositoryDep) -> list[SubjectResponse]:
    """Get all subjects"""
    subjects = repository.get_all()
    return SubjectResponse.from_subject_list(subjects)


@router.get("/{subject_id}")
async def get_subject(
    subject_id: int, repository: SubjectRepositoryDep
) -> SubjectResponse:
    """Get a subject"""
    subject = repository.get_by_id(id=subject_id)
    return SubjectResponse.from_subject(subject)


@router.post("/crawl")
async def crawl_subjects(
    building: BuildingDep, session: SessionDep, subjects_list: list[str] = embed
) -> list[Subject]:
    subjects = await SubjectRepository.crawler_create_many(
        building=building, session=session, subjects_codes=subjects_list
    )
    return subjects


@router.post("")
async def create_subject(
    subject_input: SubjectRegister, session: SessionDep
) -> SubjectResponse:
    """Create a subject"""
    subject = SubjectRepository.create(input=subject_input, session=session)
    return SubjectResponse.from_subject(subject)


@router.put("/{subject_id}")
async def update_subject(
    subject_id: int, subject_input: SubjectUpdate, session: SessionDep
) -> SubjectResponse:
    """Update a subject"""
    subject = SubjectRepository.update(
        id=subject_id, input=subject_input, session=session
    )
    return SubjectResponse.from_subject(subject)


@router.delete("/{subject_id}")
async def delete_subject(subject_id: int, session: SessionDep) -> Response:
    """Delete a subject"""
    SubjectRepository.delete(id=subject_id, session=session)
    return NoContent
