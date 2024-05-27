from datetime import datetime
from fastapi import HTTPException, status
from sqlmodel import col, select
from server.deps.session_dep import SessionDep
from server.models.database.holiday_category_db_model import HolidayCategory
from server.models.database.holiday_db_model import Holiday
from server.models.database.user_db_model import User
from server.models.http.requests.holiday_request_models import (
    HolidayRegister,
    HolidayUpdate,
)
from server.repositories.holidays_categories_repository import HolidayCategoryRepository


class HolidayRepository:
    @staticmethod
    def get_all(*, session: SessionDep) -> list[Holiday]:
        statement = select(Holiday)
        holidays = session.exec(statement).all()
        return list(holidays)

    @staticmethod
    def get_by_id(*, id: str, session: SessionDep) -> Holiday:
        statement = select(Holiday).where(col(Holiday.id) == id)
        holiday = session.exec(statement).one()
        return holiday

    @staticmethod
    def check_date_is_valid(
        *, category_id: str, date: datetime, session: SessionDep
    ) -> bool:
        statement = select(HolidayCategory).where(
            col(HolidayCategory.id) == category_id and col(Holiday.date) == date
        )
        result = session.exec(statement).first()
        return result is None

    @staticmethod
    def create(
        *, creator: User, input: HolidayRegister, session: SessionDep
    ) -> Holiday:
        if not HolidayRepository.check_date_is_valid(
            category_id=input.category_id, date=input.date, session=session
        ):
            raise HolidayInCategoryAlreadyExists(
                input.date.strftime("%d/%m/%Y"), input.category_id
            )

        category = HolidayCategoryRepository.get_by_id(
            id=input.category_id, session=session
        )
        new_holiday = Holiday(
            date=input.date,
            category=category,
            updated_at=datetime.now(),
            created_by=creator,
        )
        session.add(new_holiday)
        session.commit()
        session.refresh(new_holiday)
        return new_holiday

    @staticmethod
    def update(
        *, id: str, input: HolidayUpdate, user: User, session: SessionDep
    ) -> Holiday:
        holiday = HolidayRepository.get_by_id(id=id, session=session)
        if holiday.created_by_id != user.id:
            raise HolidayOperationNotAllowed("update", input.date.strftime("%d/%m/%Y"))
        holiday.date = input.date
        holiday.updated_at = datetime.now()
        session.add(holiday)
        session.commit()
        return holiday

    @staticmethod
    def delete(*, id: str, user: User, session: SessionDep) -> None:
        holiday = HolidayRepository.get_by_id(id=id, session=session)
        if holiday.created_by_id != user.id:
            raise HolidayOperationNotAllowed(
                "delete", holiday.date.strftime("%d/%m/%Y")
            )


class HolidayInCategoryAlreadyExists(HTTPException):
    def __init__(self, holiday_info: str, category_info: str) -> None:
        super().__init__(
            status.HTTP_409_CONFLICT,
            f"Holiday {holiday_info} in Category {category_info} already exists",
        )


class HolidayOperationNotAllowed(HTTPException):
    def __init__(self, operation: str, holiday_info: str) -> None:
        super().__init__(
            status.HTTP_401_UNAUTHORIZED,
            f"Not Allowed to {operation} Holiday {holiday_info}",
        )
