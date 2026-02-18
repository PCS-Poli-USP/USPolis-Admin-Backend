from fastapi import APIRouter, Body, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.curriculum_request_models import CurriculumRegister, CurriculumUpdate
from server.repositories.curriculum_repository import CurriculumRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/curriculums", tags=["Curriculums"])


@router.post("")
def create_curriculum(
    input: CurriculumRegister, session: SessionDep, user: UserDep,
) -> JSONResponse:
    """Create new curriculum"""

    try:
        CurriculumRepository.create(input=input, user=user, session=session)
        session.commit()
    except IntegrityError:
        session.rollback()
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Currículo criado com sucesso",
        },
    )

@router.put("/{curriculum_id}")
def update_curriculum(
    curriculum_id: int, input: CurriculumUpdate, session: SessionDep, user: UserDep,
) -> JSONResponse:
    """Update a curriculum by id"""

    try:
        CurriculumRepository.update(id=curriculum_id, input=input, user=user, session=session)
        session.commit()
    except IntegrityError:
        session.rollback()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Currículo atualizado com sucesso",
        },
    )

@router.delete("/{curriculum_id}")
def delete_curriculum(
    curriculum_id: int, session: SessionDep
) -> JSONResponse:
    """Delete a curriculum by id"""
    CurriculumRepository.delete(id=curriculum_id, session=session)
    session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Currículo removido com sucesso",
        },
    )