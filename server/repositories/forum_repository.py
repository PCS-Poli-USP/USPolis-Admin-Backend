from datetime import datetime

from sqlmodel import Session, col, select
from server.models.database.forum_db_model import ForumPost

class ForumRepository:
    @staticmethod
    def create(
        *, input: ForumPost,
        session: Session
    ) -> ForumPost:
        new_post = input
        new_post.created_at = datetime.now()

        session.add(new_post)
        session.commit()
        session.refresh(new_post)
        return new_post


    @staticmethod
    def get_all_posts(*,class_id: int, session: Session) -> list[ForumPost]:
        statement = select(ForumPost).where(col(ForumPost.class_id)==class_id)
        posts = session.exec(statement).all()
        return list(posts)
