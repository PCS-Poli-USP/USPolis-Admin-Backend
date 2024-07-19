from sqlmodel import Session, select

from server.models.database.mobile_comments_db_model import Comment


class CommentRepository:
    @staticmethod
    def create(*, new_comment: Comment, session: Session) -> Comment:
        session.add(new_comment)
        session.commit()
        session.refresh(new_comment)
        return new_comment

    @staticmethod
    def get_all(*, session: Session) -> list[Comment]:
        statement = select(Comment)
        comments = session.exec(statement).all()
        return list(comments)