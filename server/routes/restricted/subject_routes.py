from fastapi import APIRouter, Body, Response

from server.deps.authenticate import BuildingDep
from server.deps.repository_adapters.subject_repository_adapter import (
    SubjectRepositoryDep,
)
from server.deps.session_dep import SessionDep
from server.models.http.requests.subject_request_models import (
    CrawlSubject,
    SubjectRegister,
    SubjectUpdate,
    UpdateCrawlSubject,
)
from server.models.http.responses.generic_responses import NoContent
from server.models.http.responses.subject_response_models import (
    SubjectCrawlResponse,
    SubjectResponse,
)
from server.repositories.subject_repository import SubjectRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.get("/{subject_id}")
def get_subject(subject_id: int, repository: SubjectRepositoryDep) -> SubjectResponse:
    """Get a subject"""
    subject = repository.get_by_id(id=subject_id)
    return SubjectResponse.from_subject(subject)


@router.post("/crawl")
async def crawl_subjects(
    building: BuildingDep, session: SessionDep, input: CrawlSubject
) -> SubjectCrawlResponse:
    response = await SubjectRepository.crawler_create_many(
        building=building,
        session=session,
        calendar_ids=input.calendar_ids,
        subjects_codes=input.subject_codes,
    )
    return response


@router.patch("/crawl")
async def update_crawl_subjects(
    session: SessionDep,
    input: UpdateCrawlSubject,
) -> SubjectCrawlResponse:
    response = await SubjectRepository.crawler_update_many(input.subject_codes, session)
    return response


@router.post("")
def create_subject(
    subject_input: SubjectRegister, session: SessionDep
) -> SubjectResponse:
    """Create a subject"""
    subject = SubjectRepository.create(input=subject_input, session=session)
    return SubjectResponse.from_subject(subject)


@router.put("/{subject_id}")
def update_subject(
    subject_id: int, subject_input: SubjectUpdate, session: SessionDep
) -> SubjectResponse:
    """Update a subject"""
    subject = SubjectRepository.update(
        id=subject_id, input=subject_input, session=session
    )
    return SubjectResponse.from_subject(subject)


@router.delete("/{subject_id}")
def delete_subject(subject_id: int, session: SessionDep) -> Response:
    """Delete a subject"""
    SubjectRepository.delete(id=subject_id, session=session)
    return NoContent
