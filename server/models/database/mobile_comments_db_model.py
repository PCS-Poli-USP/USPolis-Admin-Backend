from datetime import datetime
from sqlmodel import Field, SQLModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

class Comment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    comment: str = Field()
    email: str | None = Field(default=None, nullable=True,)
    created_by_id: int | None = Field(
        foreign_key="mobileuser.id",
        default=None,
        nullable=True,
    )
    created_at: datetime = Field(default=datetime.now())
