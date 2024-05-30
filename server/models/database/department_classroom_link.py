from sqlmodel import SQLModel, Field


class DepartmentClassroomLink(SQLModel, table=True):
    department_id: int | None = Field(
        foreign_key="department.id", primary_key=True, default=True)
    classroom_id: int | None = Field(
        foreign_key="classroom.id", primary_key=True, default=True)
