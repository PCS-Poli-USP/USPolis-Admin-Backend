from pydantic import BaseModel

from server.models.database.classroom_db_model import Classroom
from server.models.database.department_db_model import Department
from server.models.database.subject_db_model import Subject
from server.models.http.exceptions.responses_exceptions import UnfetchDataError


class DepartmentBaseResponse(BaseModel):
    id: int
    name: str
    abbreviation: str
    professors: list[str]
    building: str

    @classmethod
    def from_department(cls, department: Department) -> "DepartmentBaseResponse":
        if department.id is None:
            raise UnfetchDataError("Department", "ID")
        return cls(
            id=department.id,
            name=department.name,
            abbreviation=department.abbreviation,
            professors=department.professors,
            building=department.building.name,
        )


class DepartmentResponse(DepartmentBaseResponse):
    subjects: list[Subject] | None
    classrooms: list[Classroom] | None

    @classmethod
    def from_department(cls, department: Department) -> "DepartmentResponse":
        if department.id is None:
            raise UnfetchDataError("Department", "ID")
        return cls(
            id=department.id,
            name=department.name,
            abbreviation=department.abbreviation,
            professors=department.professors,
            building=department.building.name,
            subjects=department.subjects,
            classrooms=department.classrooms,
        )

    @classmethod
    def from_department_list(
        cls, departments: list[Department]
    ) -> list["DepartmentResponse"]:
        return [cls.from_department(department) for department in departments]
