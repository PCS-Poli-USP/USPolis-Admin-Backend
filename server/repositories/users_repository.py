from sqlmodel import Session

from server.models.database.user_db_model import User
from server.models.http.requests.user_request_models import UserRegister


class UserRepository:
    @staticmethod
    def create_user(*, user_in: UserRegister, session: Session) -> User:
        db_user = User.model_validate(user_in)
        session.add(db_user)
        session.commit()
        return db_user
