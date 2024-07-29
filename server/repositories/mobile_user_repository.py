from sqlmodel import Session, col, select
from server.models.database.mobile_user_db_model import MobileUser


class MobileUserRepository:
    @staticmethod
    def create(*, new_user: MobileUser, session: Session) -> MobileUser:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user

    @staticmethod
    def get_user_by_sub(*, sub: str, session: Session) -> MobileUser:
        statement = select(MobileUser).where(col(MobileUser.sub) == sub)
        user = session.exec(statement).one()
        return user

    @staticmethod
    def get_user_by_id(*, id: int, session: Session) -> MobileUser:
        statement = select(MobileUser).where(col(MobileUser.id) == id)
        user = session.exec(statement).one()
        return user
