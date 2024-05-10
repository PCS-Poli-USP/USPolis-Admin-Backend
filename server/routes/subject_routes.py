from fastapi import APIRouter, Body, Depends, HTTPException, status

from server.models.database.subject_db_model import Subject
from server.models.http.requests.subject_request_models import SubjectRegister
from server.services.auth.authenticate import authenticate

embed = Body(..., embed=True)

router = APIRouter(
    prefix="/subjects", tags=["Subjects"], dependencies=[Depends(authenticate)]
)


@router.get("")
async def get_all_subjects() -> list[Subject]:
    """Get all subjects"""
    return await Subject.find_all().to_list()


@router.get("/{subject_id}")
async def get_subject(subject_id: str) -> Subject:
    """Get a subject"""
    return await Subject.by_id(subject_id)  # type: ignore


@router.post("")
async def create_subject(subject_input: SubjectRegister) -> str:
    """Create a subject"""
    if await Subject.check_code_exists(subject_input.code):
        raise SubjectCodeAlreadyExists(subject_input.code)

    subject = Subject(
        name=subject_input.name,
        code=subject_input.code,
        professors=subject_input.professors,
        type=subject_input.type,
        class_credit=subject_input.class_credit,
        work_credit=subject_input.work_credit,
        activation=subject_input.activation,
        desactivation=subject_input.desactivation,
    )
    await subject.create()
    return str(subject.id)


@router.patch("/{subject_id}")
async def update_subject(subject_id: str, subject_input: SubjectRegister) -> str:
    """Update a subject"""
    if not await Subject.check_code_is_valid(subject_id, subject_input.code):
        raise SubjectCodeAlreadyExists(subject_input.code)
    new_subject = await Subject.by_id(subject_id)
    await new_subject.update({"$set": subject_input})
    return str(new_subject.id)


@router.delete("/{subject_id}")
async def delete_subject(subject_id: str) -> int:
    """Delete a subject"""
    subject = await Subject.by_id(subject_id)
    response = await subject.delete()  # type: ignore
    if response is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "No subject deleted")
    return int(response.deleted_count)


class SubjectCodeAlreadyExists(HTTPException):
    def __init__(self, subject_code: str) -> None:
        super().__init__(
            status.HTTP_409_CONFLICT, f"Subject {subject_code} already exists"
        )
        super().__init__(
            status.HTTP_409_CONFLICT, f"Subject {subject_code} already exists"
        )
