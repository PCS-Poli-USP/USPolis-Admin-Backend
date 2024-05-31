from datetime import datetime
from typing import TYPE_CHECKING
from fastapi import HTTPException, status
from sqlmodel import Session, col, select

from server.models.database.department_db_model import Department
from server.models.http.requests.department_request_models import DepartmentCreate
from server.repositories.buildings_repository import BuildingRepository

if TYPE_CHECKING:
    from server.repositories.subject_repository import SubjectRepository


class DepartmentRepository:
    @staticmethod
    def get_all(*, session: Session) -> list[Department]:
        statement = select(Department)
        departments = session.exec(statement).all()
        return list(departments)

    @staticmethod
    def get_by_id(*, id: int, session: Session) -> Department:
        statement = select(Department).where(col(Department.id) == id)
        department = session.exec(statement).first()
        if department is None:
            raise DepartmentNotExists(str(id))
        return department

    @staticmethod
    def create(*, input: DepartmentCreate, session: Session) -> Department:
        building = BuildingRepository.get_by_id(
            building_id=input.building_id, session=session
        )
        subjects = None
        if input.subjects_ids is not None:
            subjects = SubjectRepository.get_by_ids(
                ids=input.subjects_ids, session=session
            )
        new_department = Department(
            name=input.name,
            abbreviation=input.abbreviation,
            professors=input.professors,
            building=building,
            subjects=subjects,
            updated_at=datetime.now(),
        )
        session.add(new_department)
        session.commit()
        session.refresh(new_department)
        return new_department


class DepartmentNotExists(HTTPException):
    def __init__(self, department_info: str) -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND, f"Department with {department_info} not exists"
        )
