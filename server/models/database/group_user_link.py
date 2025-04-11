from sqlmodel import Field, SQLModel


class GroupUserLink(SQLModel, table=True):
    group_id: int | None = Field(
        default=None, primary_key=True, foreign_key="group.id", ondelete="CASCADE"
    )
    user_id: int | None = Field(
        default=None, primary_key=True, foreign_key="user.id", ondelete="CASCADE"
    )
