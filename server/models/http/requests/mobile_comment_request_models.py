from pydantic import BaseModel

from server.models.database.mobile_comments_db_model import Comment


class MobileCommentRegister(BaseModel):
    comment: str
    email: str | None = None
    created_by: int | None = None


def to_comment_model(c: MobileCommentRegister) -> Comment:
    return Comment(comment=c.comment, email=c.email, created_by_id=c.created_by)
