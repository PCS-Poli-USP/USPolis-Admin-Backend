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
        subject_id=postDTO.subject_id
    )

def to_forumreply_model(post_id: int, replyDTO: ForumPostRegister) -> ForumPost:
    return ForumPost(
        class_id=replyDTO.class_id,
        content=replyDTO.content,
        user_id=replyDTO.user_id,
        subject_id=replyDTO.subject_id,
        reply_of_post_id=post_id
    )

class ForumReportRegister(BaseModel):
    post_id: int
    user_id: int

class ForumPostLike(BaseModel):
    post_id: int
    user_id: int
    like_state: bool

class ForumUserLikesRegister(BaseModel):
    user_id: int