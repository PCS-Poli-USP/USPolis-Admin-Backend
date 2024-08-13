from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, select
from server.models.database.forum_db_model import ForumPost, ForumPostReply

class ForumRepository:
    @staticmethod
    def create(*, input: ForumPost, session: Session) -> ForumPost:
        new_post = input
        #new_post.created_at = datetime.now()
        new_post.report_count = 0
        # new_post.reported_users = []

        session.add(new_post)
        session.commit()
        session.refresh(new_post)
        return new_post

    @staticmethod
    def get_all_posts(*, subject_id: int, session: Session) -> list[ForumPost]:
        statement = select(ForumPost).where(col(ForumPost.subject_id)==subject_id)
        posts = session.exec(statement).all()
        return list(posts)

    @staticmethod
    def get_post_by_id(*, post_id: int, session: Session) -> ForumPost:
        statement = select(ForumPost).where(col(ForumPost.id) == post_id)
        post = session.exec(statement).one()
        return post

    @staticmethod
    def update_forum_report_count(
        *, post_id: int, mobile_user_id: int, session: Session
    ) -> ForumPost:
        statement = select(ForumPost).where(col(ForumPost.id) == post_id)
        post = session.exec(statement).one()

        # user_statement = select(MobileUser).where(col(MobileUser.id)==mobile_user_id)
        # reported_mobile_user = session.exec(user_statement).first()
        post.report_count += 1

        session.add(post)
        session.commit()
        session.refresh(post)

        return post

    @staticmethod
    def create_reply(*, input: ForumPostReply, session: Session):
        session.add(input)
        
        try:
            session.commit()
        except IntegrityError:
            raise PostNotFoundException(input.forum_post_id)

        session.refresh(input)
        return input

    @staticmethod
    def get_all_replies(*, post_id: int ,session: Session):
        statement = select(ForumPostReply).where(col(ForumPostReply.forum_post_id)==post_id)
        replies = session.exec(statement).all()
        return list(replies)

class PostNotFoundException(HTTPException):
    def __init__(self, post_id: int) -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND, f"Forum Post {post_id} does not exists"
        )
