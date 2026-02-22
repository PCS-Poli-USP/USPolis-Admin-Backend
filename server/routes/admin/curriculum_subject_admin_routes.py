from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.curriculum_subject_request_models import CurriculumSubjectRegister, CurriculumSubjectUpdate
from server.repositories.curriculum_subject_repository import CurriculumSubjectRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/curriculum_subjects", tags=["CurriculumSubjects"])


@router.post("")
def create_curriculum_subject(
    input: CurriculumSubjectRegister, session: SessionDep, user: UserDep,
) -> JSONResponse:
    """Create new curriculum subject"""

    try:
        CurriculumSubjectRepository.create(input=input, user=user, session=session)
        session.commit()
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Disciplina do currículo criada com sucesso",
            },
        )
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail="Não foi possível criar a disciplina do currículo",
        )

@router.put("/{curriculum_subject_id}")
def update_curriculum_subject(
    curriculum_subject_id: int, input: CurriculumSubjectUpdate, session: SessionDep, user: UserDep,
) -> JSONResponse:
    """Update a curriculum subject by id"""
    try:
        CurriculumSubjectRepository.update(id=curriculum_subject_id, input=input, user=user, session=session)
        session.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Disciplina do currículo atualizada com sucesso",
            },
        )
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail="Não foi possível atualizar a disciplina do currículo",
        )

@router.delete("/{curriculum_subject_id}")
def delete_curriculum_subject(
    curriculum_subject_id: int, session: SessionDep
) -> JSONResponse:
    """Delete a curriculum subject by id"""
    CurriculumSubjectRepository.delete(id=curriculum_subject_id, session=session)
    session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Disciplina do currículo removida com sucesso",
        },
    )
