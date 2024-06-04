from fastapi import APIRouter

from server.deps.session_dep import SessionDep
from server.models.http.responses.department_response_models import DepartmentResponse
from server.repositories.department_repository import DepartmentRepository

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("")
async def get_all_departments(session: SessionDep) -> list[DepartmentResponse]:
    departments = DepartmentRepository.get_all(session=session)
    return DepartmentResponse.from_department_list(departments)


@router.get("/{department_id}")
async def get_department(department_id: int, session: SessionDep) -> DepartmentResponse:
    department = DepartmentRepository.get_by_id(id=department_id, session=session)
    return DepartmentResponse.from_department(department)
