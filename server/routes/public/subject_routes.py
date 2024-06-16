from fastapi import APIRouter, Body, Response

from server.deps.authenticate import BuildingDep
from server.deps.session_dep import SessionDep
from server.models.database.subject_db_model import Subject
from server.models.http.requests.subject_request_models import (
    SubjectRegister,
    SubjectUpdate,
)
from server.models.http.responses.generic_responses import NoContent
from server.models.http.responses.subject_response_models import SubjectResponse
from server.repositories.subject_repository import SubjectRepository
from server.services.jupiter_crawler.crawler import JupiterCrawler
from tests.services.jupiter_crawler.crawler_test_utils import JupiterCrawlerTestUtils

embed = Body(..., embed=True)

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.get("", response_model_by_alias=False)
async def get_all_subjects(session: SessionDep) -> list[SubjectResponse]:
    """Get all subjects"""
    subjects = SubjectRepository.get_all(session=session)
    return SubjectResponse.from_subject_list(subjects)


@router.get("/{subject_id}", response_model_by_alias=False)
async def get_subject(subject_id: int, session: SessionDep) -> SubjectResponse:
    """Get a subject"""
    subject = SubjectRepository.get_by_id(id=subject_id, session=session)
    return SubjectResponse.from_subject(subject)


@router.get("/crawl/{subject_code}")
async def crawl_subject(
    subject_code: str, building: BuildingDep, session: SessionDep
) -> Subject:
    # TODO: remover o content quando jupiter voltar ao normal!
    contents = JupiterCrawlerTestUtils.retrieve_html_contents()
    content = contents[subject_code]
    subject = await JupiterCrawler.crawl_subject_static(subject_code, content)
    return SubjectRepository.crawler_create(
        subject=subject, session=session, building=building
    )


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
