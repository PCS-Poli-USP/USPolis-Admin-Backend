from fastapi import HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, col, desc, select

from server.models.database.feedback_db_model import Feedback
from server.models.database.user_db_model import User
from server.models.http.requests.feedback_request_models import FeedbackRegister
from server.models.page_models import Page, PaginationInput
from server.utils.must_be_int import must_be_int


class FeedbackRepository:
    @staticmethod
    def get_all(*, session: Session) -> list[Feedback]:
        statement = select(Feedback)
        return list(session.exec(statement).all())

    @staticmethod
    def get_all_paginated(
        *, pagination: PaginationInput, session: Session
    ) -> Page[Feedback]:
        statement = select(Feedback).order_by(desc(col(Feedback.created_at)))
        return Page.paginate(statement, pagination, session)

    @staticmethod
    def get_by_id(*, id: int, session: Session) -> Feedback:
        statement = select(Feedback).where(col(Feedback.id) == id)
        try:
            feedback = session.exec(statement).one()
        except NoResultFound:
            raise FeedbackNotFound(id)
        return feedback

    @staticmethod
    def create(*, input: FeedbackRegister, user: User, session: Session) -> Feedback:
        feedback = Feedback(
            user_id=must_be_int(user.id),
            user=user,
            title=input.title,
            message=input.message,
        )
        session.add(feedback)
        return feedback


class FeedbackNotFound(HTTPException):
    def __init__(self, id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Não foi possível encontrar Feedback com id {id}",
        )
