from sqlmodel import Field, SQLModel


class ForumPostReactsLink(SQLModel, table=True):
    forum_post_id: int = Field(
        default=0, foreign_key="forumpost.id", primary_key=True, ondelete="CASCADE"
    )
    mobile_user_id: int | None = Field(
        default=None, foreign_key="mobileuser.id", primary_key=True, ondelete="CASCADE"
    )
    post_like: bool = Field(default=False)
