from fastapi import APIRouter, Body, Response

from server.deps.session_dep import SessionDep
from server.models.http.requests.class_request_models import ClassRegister, ClassUpdate
from server.models.http.responses.class_response_models import ClassResponse
from server.models.http.responses.generic_responses import NoContent
from server.repositories.class_repository import ClassRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/classes", tags=["Classes"])


@router.get("")
async def get_all_classes(session: SessionDep) -> list[ClassResponse]:
    """Get all classes"""
    classes = ClassRepository.get_all(session=session)
    return ClassResponse.from_class_list(classes)


@router.get("/{class_id}")
async def get_class(class_id: int, session: SessionDep) -> ClassResponse:
    """Get a class by id"""
    university_class = ClassRepository.get_by_id(id=class_id, session=session)
    return ClassResponse.from_class(university_class)


@router.post("")
async def create_class(
    class_input: ClassRegister, session: SessionDep
) -> ClassResponse:
    """Create a class"""
    university_class = ClassRepository.create(input=class_input, session=session)
    return ClassResponse.from_class(university_class)


@router.put("/{class_id}")
async def update_class(
    class_id: int, class_input: ClassUpdate, session: SessionDep
) -> ClassResponse:
    """Update a class by id"""
    updated_class = ClassRepository.update(
        id=class_id, input=class_input, session=session
    )
    return ClassResponse.from_class(updated_class)


@router.delete("/{class_id}")
async def delete_class(class_id: int, session: SessionDep) -> Response:
    """Delete a class by id"""
    ClassRepository.delete(id=class_id, session=session)
    return NoContent
