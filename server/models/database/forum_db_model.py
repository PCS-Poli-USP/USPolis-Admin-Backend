from datetime import datetime

from sqlalchemy import func
from sqlmodel import Field, Relationship, SQLModel

from server.models.database.mobile_user_db_model import MobileUser


class ForumPost(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    class_id : int = Field(
        foreign_key = "class.id"
    )

    subject_id : int = Field(
        foreign_key = "subject.id"
    )
    content : str | None = Field()

    user_id : int = Field(
        foreign_key = "mobileuser.id", default=None, nullable=False
    )

    user: "MobileUser" = Relationship()

    created_at : datetime = Field(default=datetime.now())
    
    # reported_users : list[MobileUser] = Relationship(back_populates="id")

    report_count : int = Field(default=0)
