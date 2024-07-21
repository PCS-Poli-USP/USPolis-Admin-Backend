from datetime import datetime
from pydantic import BaseModel

from server.models.database.mobile_comments_db_model import Comment


class MobileCommentRegister(BaseModel):
    comment: str
    email: str | None
    

def to_comment_model(c: MobileCommentRegister) -> Comment:
    return Comment(
        comment=c.comment,
        email=c.email
    )

class MobileCommentResponse(MobileCommentRegister):
    created_at: datetime

    
    @classmethod
    def from_model(c, comment: Comment):
        return c(
            comment=comment.comment,
            email=comment.email,
            created_at=comment.created_at
        )
    
    @classmethod
    def from_model_list(c, comments: list[Comment]) -> list["MobileCommentResponse"]:
        return [c.from_model(comment) for comment in comments]
