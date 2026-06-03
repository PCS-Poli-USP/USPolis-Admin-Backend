from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.course_request_models import (
    CourseRegister,
    CourseUpdate,
)
from server.repositories.course_repository import CourseRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/courses", tags=["Courses"])

def normalize_course_name(name: str) -> str:
    return name.strip()

@router.post("")
def create_course(
    input: CourseRegister,
    session: SessionDep,
    user: UserDep,
) -> JSONResponse:
    """Create new course"""

    input.name = normalize_course_name(input.name)

    existing = CourseRepository.get_by_name_ignore_case(
        input.name,
        session,
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Já existe um curso com esse nome",
        )
    
    try:
        CourseRepository.create(
            input=input,
            user=user,
            session=session,
        )

        session.commit()

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "detail": "Curso criado com sucesso",
            },
        )

    except IntegrityError as e:
        session.rollback()

        if "course_name_key" in str(e):
            raise HTTPException(
                status_code=400,
                detail="Já existe um curso com esse nome",
            )

        raise HTTPException(
            status_code=400,
            detail="Não foi possível criar o curso",
        )


@router.put("/{course_id}")
def update_course(
    course_id: int,
    input: CourseUpdate,
    session: SessionDep,
    user: UserDep,
) -> JSONResponse:
    """Update a course by id"""

    input.name = normalize_course_name(input.name)

    existing = CourseRepository.get_by_name_ignore_case(
        input.name,
        session,
    )

    if existing and existing.id != course_id:
        raise HTTPException(
            status_code=400,
            detail="Já existe um curso com esse nome",
        )
    
    try:
        CourseRepository.update(
            id=course_id,
            input=input,
            user=user,
            session=session,
        )

        session.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "detail": "Curso atualizado com sucesso",
            },
        )
    

    except IntegrityError as e:
        session.rollback()

        if "course_name_key" in str(e):
            raise HTTPException(
                status_code=400,
                detail="Já existe um curso com esse nome",
            )

        raise HTTPException(
            status_code=400,
            detail="Não foi possível atualizar o curso",
        )


@router.delete("/{course_id}")
def delete_course(
    course_id: int,
    session: SessionDep,
) -> JSONResponse:
    """Delete a course by id"""

    CourseRepository.delete(
        id=course_id,
        session=session,
    )

    session.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "detail": "Curso removido com sucesso",
        },
    )