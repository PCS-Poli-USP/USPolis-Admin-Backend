from sqlmodel import SQLModel, Field

class CourseOptions(SQLModel, table=True):
    codcur: int = Field(primary_key=True)
    codhab: int = Field(primary_key=True)
    name: str