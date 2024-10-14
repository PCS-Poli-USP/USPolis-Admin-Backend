from fastapi import HTTPException, status
from sqlmodel import Session, col, select

from server.models.database.holiday_category_db_model import HolidayCategory
from server.models.database.user_db_model import User
from server.models.http.requests.holiday_category_request_models import (
    HolidayCategoryRegister,
    HolidayCategoryUpdate,
)


class HolidayCategoryRepository:
    @staticmethod
    def get_all(*, session: Session) -> list[HolidayCategory]:
        statement = select(HolidayCategory)
        holidays_categories = session.exec(statement).all()
        return list(holidays_categories)

    @staticmethod
    def get_by_id(*, id: int, session: Session) -> HolidayCategory:
        statement = select(HolidayCategory).where(col(HolidayCategory.id) == id)
        holiday_category = session.exec(statement).one()
        return holiday_category

    @staticmethod
    def get_by_ids(*, ids: list[int], session: Session) -> list[HolidayCategory]:
        statement = select(HolidayCategory).where(col(HolidayCategory.id).in_(ids))
        holidays_categories = session.exec(statement).all()
        return list(holidays_categories)

    @staticmethod
    def get_by_name(*, name: str, session: Session) -> HolidayCategory:
        statement = select(HolidayCategory).where(col(HolidayCategory.name) == name)
        holiday_category = session.exec(statement).one()
        return holiday_category

    @staticmethod
    def create(
        *, creator: User, input: HolidayCategoryRegister, session: Session
    ) -> HolidayCategory:
        new_holiday_category = HolidayCategory(
            name=input.name,
            created_by=creator,
        )
        session.add(new_holiday_category)
        session.commit()
        session.refresh(new_holiday_category)
        return new_holiday_category

    @staticmethod
    def update(
        *, id: int, input: HolidayCategoryUpdate, user: User, session: Session
    ) -> HolidayCategory:
        holiday_category = HolidayCategoryRepository.get_by_id(id=id, session=session)
        if not user.is_admin and holiday_category.created_by_id != user.id:
            raise HolidayCategoryOperationNotAllowed("update", holiday_category.name)
        holiday_category.name = input.name
        session.add(holiday_category)
        session.commit()
        return holiday_category

    @staticmethod
    def delete(*, id: int, user: User, session: Session) -> None:
        holiday_category = HolidayCategoryRepository.get_by_id(id=id, session=session)
        if not user.is_admin and holiday_category.created_by_id != user.id:
            raise HolidayCategoryOperationNotAllowed("delete", holiday_category.name)
        session.delete(holiday_category)
        session.commit()


class HolidayCategoryOperationNotAllowed(HTTPException):
    def __init__(self, operation: str, holiday_category_info: str) -> None:
        super().__init__(
            status.HTTP_401_UNAUTHORIZED,
            f"Only the creator is Allowed to {operation} HolidayCategory {holiday_category_info}",
        )
