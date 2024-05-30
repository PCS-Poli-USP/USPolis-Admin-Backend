from sqlmodel import Field, SQLModel


class SubjectBuildingLink(SQLModel, table=True):
    subject_id: int | None = Field(
        default=None, foreign_key="subject.id", primary_key=True)
    building_id: int | None = Field(
        default=None, foreign_key="building.id", primary_key=True)
