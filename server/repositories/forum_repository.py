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
            class_id = input.class_id,
            post_title = input.post_title,
            post_content = input.post_content,
            created_at = datetime.now()
        )

        session.add(new_post)
        session.commit()
        session.refresh(new_post)
        return new_post


    @staticmethod
    def get_all(*,class_id: int, session: Session) -> list[ForumPost]:
        statement = select(ForumPost).where(class_id=class_id)
        posts = session.exec(statement).all()
        return list(posts)