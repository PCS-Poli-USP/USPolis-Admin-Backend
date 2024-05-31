from pydantic import BaseModel


class DepartmentCreate(BaseModel):
    building_id: int
    name: str
    abbreviation: str
    professors: list[str]
    subjects_ids: list[int] | None
    classrooms_ids: list[int] | None


class DepartmentUpdate(DepartmentCreate):
    pass
