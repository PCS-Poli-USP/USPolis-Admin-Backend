from sqlmodel import Field, SQLModel


class GroupClassroomLink(SQLModel, table=True):
    group_id: int | None = Field(
        default=None, primary_key=True, foreign_key="group.id", ondelete="CASCADE"
    )
    classroom_id: int | None = Field(
        default=None, primary_key=True, foreign_key="classroom.id", ondelete="CASCADE"
    )
