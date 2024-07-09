from datetime import datetime

from pydantic import BaseModel
from server.models.database.forum_db_model import ForumPost
from server.models.http.exceptions.responses_exceptions import UnfetchDataError

class ForumPostResponse(BaseModel):
    id: int
    class_id : int

    # title = str | None = Field ()
    content : str | None

    author : str 
    # user_id : int = Field(
    #     foreign_key = "user.id"
    # )

    created_at : datetime

    @classmethod
    def from_forum_post(
        cls, post: ForumPost
    ) -> "ForumPostResponse":
        if post.id is None:
            raise UnfetchDataError("Forum Post", "ID")
        return cls(
            id= post.id,
            class_id= post.class_id,
            content= post.content,
            author= post.author,
        )

    @classmethod
    def from_forum_post_list(
        cls, posts: list[ForumPost]
    ) -> list["ForumPostResponse"]:
        return [cls.from_forum_post(post) for post in posts]