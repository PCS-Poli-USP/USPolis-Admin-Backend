from datetime import datetime
from pydantic import BaseModel

from server.models.database.mobile_comments_db_model import Comment

class MobileCommentResponse(BaseModel):
    comment: str
    email: str | None
    created_at: datetime

    @classmethod
    def from_model(cls, comment: Comment) -> "MobileCommentResponse":
        return cls(
            comment=comment.comment, email=comment.email, created_at=comment.created_at
        )

    @classmethod
    def from_model_list(cls, comments: list[Comment]) -> list["MobileCommentResponse"]:
        return [cls.from_model(comment) for comment in comments]
