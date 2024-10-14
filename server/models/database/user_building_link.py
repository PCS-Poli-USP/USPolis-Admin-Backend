from sqlmodel import Field, SQLModel


class UserBuildingLink(SQLModel, table=True):
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    building_id: int | None = Field(
        default=None, foreign_key="building.id", primary_key=True
    )
