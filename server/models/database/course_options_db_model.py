from sqlmodel import Field, SQLModel


class CourseOptions(SQLModel, table=True):
    codcur: int = Field(primary_key=True)
    codhab: int = Field(primary_key=True)
    name: str
