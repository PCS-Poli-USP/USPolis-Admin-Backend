from pydantic import BaseModel

from server.models.database.forum_db_model import ForumPost


class ForumPostRegister(BaseModel):
    user_id: int
    content: str
    class_id: int
    subject_id: int


def to_forumpost_model(postDTO: ForumPostRegister) -> ForumPost:
    return ForumPost(
        class_id=postDTO.class_id,
        content=postDTO.content,
        user_id=postDTO.user_id,
        subject_id=postDTO.subject_id,
    )


class ForumReportRegister(BaseModel):
    post_id: int
    user_id: int
