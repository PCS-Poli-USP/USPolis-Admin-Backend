from sqlmodel import Field, SQLModel

class ForumPostReportLink(SQLModel, table=True):
    forum_post_id: int | None = Field(default=None, foreign_key="forumpost.id", primary_key=True)
    mobile_user_id: int | None = Field(default=None, foreign_key="mobileuser.id", primary_key=True)
