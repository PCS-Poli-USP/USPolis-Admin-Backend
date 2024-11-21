from sqlmodel import Field, SQLModel


class ForumPostReactsLink(SQLModel, table=True):
    forum_post_id: int = Field(default=0, foreign_key="forumpost.id", primary_key=True)
    mobile_user_id: int | None = Field(
        default=None, foreign_key="mobileuser.id", primary_key=True
    )
    post_like: bool = Field(default=False)
