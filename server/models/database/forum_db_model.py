from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, String, UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, Relationship, SQLModel

from server.models.database.class_calendar_link import ClassCalendarLink
from server.utils.enums.class_type import ClassType
from server.models.database.class_db_model import Class 


class ForumPost(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    event_id : int = Field(
        foreign_key = "class.id"
    )

    # title = str | None = Field ()
    content : str | None = Field()

    author : str = Field()
    # user_id : int = Field(
    #     foreign_key = "user.id"
    # )

    created_at : date = Field(default=datetime.now())