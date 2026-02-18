from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.course_request_models import CourseRegister, CourseUpdate
from server.repositories.course_repository import CourseRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.post("")
def create_course(
    input: CourseRegister, session: SessionDep, user: UserDep,
) -> JSONResponse:
    """Create new course"""
    try:
        CourseRepository.create(input=input, user=user ,session=session)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise CourseAlreadyExists(name=input.name)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Curso criado com sucesso",
        },
    )


@router.put("/{course_id}")
def update_course(
    course_id: int, input: CourseUpdate, session: SessionDep, user: UserDep,
) -> JSONResponse:
    """Update a course by id"""
    try:
        CourseRepository.update(id=course_id, input=input, user=user, session=session)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise CourseAlreadyExists(name=input.name)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Curso atualizado com sucesso",
        },
    )



@router.delete("/{course_id}")
def delete_course(
    course_id: int, session: SessionDep
) -> JSONResponse:
    """Delete a course by id"""
    CourseRepository.delete(id=course_id, session=session)
    session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Curso removido com sucesso",
        },
    )


class CourseAlreadyExists(HTTPException):
    def __init__(self, name: str) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Curso com o nome {name} já existe.",
        )