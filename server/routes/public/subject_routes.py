from fastapi import APIRouter, Body, Depends, Response

from server.deps.authenticate import authenticate
from server.deps.session_dep import SessionDep
from server.models.http.requests.subject_request_models import (
    SubjectRegister,
    SubjectUpdate,
)
from server.models.http.responses.generic_responses import NoContent
from server.models.http.responses.subject_response_models import SubjectResponse
from server.repositories.subject_repository import SubjectRepository

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
