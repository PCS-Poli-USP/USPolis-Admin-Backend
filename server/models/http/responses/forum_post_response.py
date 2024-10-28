from datetime import datetime
from pydantic import BaseModel
from server.models.database.forum_db_model import ForumPost
from server.models.database.forum_post_reacts_link import ForumPostReactsLink
from sqlmodel import Session, col, select

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
    user_liked: bool| None

    @classmethod
    def from_forum_post(cls, mobile_user_id: int, post: ForumPost, session: Session) -> "ForumPostResponse":

        user_statement = select(ForumPostReactsLink).where(
            col(ForumPostReactsLink.mobile_user_id)==mobile_user_id,
            col(ForumPostReactsLink.forum_post_id)==post.id
        )

        user_liked_this_post = False
        
        if user_statement != None:
            user_like_post = session.exec(user_statement).first()

            if user_like_post != None:   
                user_liked_this_post = user_like_post.post_like



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
            user_liked = user_liked_this_post
        )

    @classmethod
    def from_forum_post_list(cls, mobile_user_id:int, posts: list[ForumPost], session:Session) -> list["ForumPostResponse"]:
        return [cls.from_forum_post(mobile_user_id, post, session) for post in posts]

class ForumPostReplyResponse(ForumPostResponse):
    reply_of_post_id: int

    @classmethod
    def from_forum_reply(cls, reply: ForumPost, mobile_user_id: int, session: Session) -> "ForumPostReplyResponse":

        user_statement = select(ForumPostReactsLink).where(
            col(ForumPostReactsLink.mobile_user_id)==mobile_user_id,
            col(ForumPostReactsLink.forum_post_id)==reply.id
        )

        user_liked_this_reply = False
        
        if user_statement != None:
            user_like_reply = session.exec(user_statement).first()

            if user_like_reply != None:   
                user_liked_this_reply = user_like_reply.post_like

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
            user_liked = user_liked_this_reply,
        )

    @classmethod
    def from_forum_post_reply_list(cls, replies: list[ForumPost], mobile_user_id: int, session: Session) -> list["ForumPostReplyResponse"]:
        return [cls.from_forum_reply(reply, mobile_user_id, session) for reply in replies]
