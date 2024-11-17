from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel

from server.models.database.forum_post_report_link import ForumPostReportLink
from server.models.database.mobile_user_db_model import MobileUser
from server.models.database.forum_post_reacts_link import ForumPostReactsLink



class ForumPost(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)

    class_id: int = Field(
        foreign_key="class.id"
    )

    subject_id : int = Field(
        foreign_key = "subject.id"
    )

    reply_of_post_id: int | None = Field(default=None)

    content : str | None = Field()

    user_id: int = Field(foreign_key="mobileuser.id", default=None, nullable=False)

    user: "MobileUser" = Relationship()

    created_at : datetime = Field(default=datetime.now(), nullable=False)
    
    reported_by_users : list[MobileUser] = Relationship(link_model=ForumPostReportLink)

    report_count: int = Field(default=0)

    replies_count: int = Field(default=0)

    enabled: bool = Field(default=True)

    liked_by_users: list[MobileUser] = Relationship(link_model=ForumPostReactsLink)

    likes_count: int = Field(default=0)

    filter_tags: int = Field(default=1)
