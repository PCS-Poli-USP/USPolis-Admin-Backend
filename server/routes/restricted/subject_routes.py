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


@router.post("/crawl")
async def crawl_subjects(
    building: BuildingDep, session: SessionDep, input: CrawlSubject
) -> SubjectCrawlResponse:
    response = await SubjectRepository.crawler_create_many(
        building=building,
        session=session,
        calendar_ids=input.calendar_ids,
        subjects_codes=input.subject_codes,
        type=input.type,
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
    subject_input: SubjectRegister, repository: SubjectRepositoryDep
) -> SubjectResponse:
    """Create a subject"""
    subject = repository.create(input=subject_input)
    return SubjectResponse.from_subject(subject)


@router.put("/{subject_id}")
def update_subject(
    subject_id: int, subject_input: SubjectUpdate, repository: SubjectRepositoryDep
) -> SubjectResponse:
    """Update a subject"""
    subject = repository.update(id=subject_id, input=subject_input)
    return SubjectResponse.from_subject(subject)


@router.delete("/{subject_id}")
def delete_subject(subject_id: int, repository: SubjectRepositoryDep) -> Response:
    """Delete a subject"""
    repository.delete(id=subject_id)
    return NoContent
