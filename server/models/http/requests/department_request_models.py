from pydantic import BaseModel


class DepartmentRegister(BaseModel):
    building_id: int
    name: str
    abbreviation: str
    professors: list[str]
    subjects_ids: list[int] | None
    classrooms_ids: list[int] | None


class DepartmentUpdate(DepartmentRegister):
    building_id: int | None  # type: ignore
