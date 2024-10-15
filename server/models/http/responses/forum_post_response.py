from datetime import datetime
from pydantic import BaseModel
from server.models.database.forum_db_model import ForumPost
from server.models.database.forum_post_reacts_link import ForumPostReactsLink

class ForumPostResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    content : str | None
    class_id : int
    subject_id: int
    created_at : datetime
    replies_count: int
    likes_count: int | None

    @classmethod
    def from_forum_post(cls, post: ForumPost) -> "ForumPostResponse":
        return cls(
            id = post.id,
            user_id = post.user_id,
            class_id = post.class_id,
            subject_id=post.subject_id, 
            content = post.content,
            user_name = post.user.given_name+" "+post.user.family_name,
            created_at = post.created_at,
            replies_count = post.replies_count,
            likes_count = post.likes_count,
        )

    @classmethod
    def from_forum_post_list(cls, posts: list[ForumPost]) -> list["ForumPostResponse"]:
        return [cls.from_forum_post(post) for post in posts]

class ForumPostReplyResponse(ForumPostResponse):
    reply_of_post_id: int

    @classmethod
    def from_forum_reply(cls, reply: ForumPost) -> "ForumPostReplyResponse":

        return cls(
            id = reply.id,
            reply_of_post_id = reply.reply_of_post_id,
            user_id = reply.user_id,
            class_id = reply.class_id,
            subject_id= reply.subject_id, 
            content = reply.content,
            user_name = reply.user.given_name+" "+reply.user.family_name,
            created_at = reply.created_at,
            replies_count = reply.replies_count,
            likes_count = reply.likes_count,
        )

    @classmethod
    def from_forum_post_reply_list(cls, replies: list[ForumPost]) -> list["ForumPostReplyResponse"]:
        return [cls.from_forum_reply(reply) for reply in replies]


class ForumUserLikesReponse(BaseModel):
    post_id: int
    like_state: bool

    @classmethod
    def from_user_forum_likes(
        cls, user_forum_like: ForumPostReactsLink
    ) -> "ForumUserLikesReponse":
        return cls(
            post_id= user_forum_like.forum_post_id,
            like_state=  user_forum_like.post_like
        )


    @classmethod
    def from_user_forum_likes_list(
        cls, user_forum_likes: list[ForumPostReactsLink]
    ) -> list["ForumUserLikesReponse"]:
        return[cls.from_user_forum_likes(user_forum_like) for user_forum_like in user_forum_likes ]