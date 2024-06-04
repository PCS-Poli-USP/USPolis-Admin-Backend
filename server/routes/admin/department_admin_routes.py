from fastapi import APIRouter, Response

from server.deps.session_dep import SessionDep
from server.models.http.requests.department_request_models import (
    DepartmentRegister,
    DepartmentUpdate,
)
from server.models.http.responses.department_response_models import DepartmentResponse
from server.models.http.responses.generic_responses import NoContent
from server.repositories.department_repository import DepartmentRepository

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.post("")
async def create_department(
    department_input: DepartmentRegister, session: SessionDep
) -> DepartmentResponse:
    department = DepartmentRepository.create(input=department_input, session=session)
    return DepartmentResponse.from_department(department)


@router.put("/{department_id}")
async def update_department(
    department_id: int, department_input: DepartmentUpdate, session: SessionDep
) -> DepartmentResponse:
    department = DepartmentRepository.update(
        id=department_id, input=department_input, session=session
    )
    return DepartmentResponse.from_department(department)


@router.delete("/{department_id}")
async def delete_department(department_id: int, session: SessionDep) -> Response:
    DepartmentRepository.delete(id=department_id, session=session)
    return NoContent
