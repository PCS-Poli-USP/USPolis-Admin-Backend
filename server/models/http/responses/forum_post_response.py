from datetime import datetime
from pydantic import BaseModel
from server.models.database.forum_db_model import ForumPost

class ForumPostResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    content : str | None
    class_id : int
    subject_id: int
    created_at : datetime

    @classmethod
    def from_forum_post(cls, post: ForumPost) -> "ForumPostResponse":
        return cls(
            id = post.id,
            user_id = post.user_id,
            class_id = post.class_id,
            subject_id=post.subject_id, 
            content = post.content,
            user_name = post.user.given_name+" "+post.user.family_name,
            created_at = post.created_at
        )

    @classmethod
    def from_forum_post_list(cls, posts: list[ForumPost]) -> list["ForumPostResponse"]:
        return [cls.from_forum_post(post) for post in posts]


# class ForumReportResponse(BaseModel):
