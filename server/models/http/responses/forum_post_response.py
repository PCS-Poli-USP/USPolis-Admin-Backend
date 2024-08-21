from datetime import datetime
from pydantic import BaseModel
from server.models.database.forum_db_model import ForumPost, ForumPostReply

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

class ForumPostReplyResponse(ForumPostResponse):
    forum_post_id: int

    @classmethod
    def from_forum_reply(cls, reply: ForumPostReply) -> "ForumPostReplyResponse":
        return cls(
            id = reply.id,
            forum_post_id = reply.forum_post_id,
            user_id = reply.user_id,
            class_id = reply.class_id,
            subject_id= reply.subject_id, 
            content = reply.content,
            user_name = reply.user.given_name+" "+reply.user.family_name,
            created_at = reply.created_at
        )

    @classmethod
    def from_forum_post_reply_list(cls, replies: list[ForumPostReply]) -> list["ForumPostReplyResponse"]:
        return [cls.from_forum_reply(reply) for reply in replies]

# class ForumReportResponse(BaseModel):
