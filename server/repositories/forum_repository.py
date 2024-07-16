from datetime import datetime

from sqlmodel import Session, col, select
from server.models.database.forum_db_model import ForumPost
from server.models.http.requests.forum_request_models import ForumPostRegister

class ForumRepository:
    @staticmethod
    def create(
        *, input: ForumPostRegister,
        session: Session
    ) -> ForumPost:
        new_post = ForumPost(
            event_id = input.event_id,
            author= input.author,
            content = input.content,
            created_at = datetime.now()
        )

        session.add(new_post)
        session.commit()
        session.refresh(new_post)
        return new_post


    @staticmethod
    def get_all_posts(*,class_id: int, session: Session) -> list[ForumPost]:
        statement = select(ForumPost).where(col(ForumPost.event_id)==class_id)
        posts = session.exec(statement).all()
        return list(posts)