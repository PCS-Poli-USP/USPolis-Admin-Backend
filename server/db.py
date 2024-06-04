from collections.abc import Generator

from sqlmodel import Session, create_engine

from server.config import CONFIG
from server.models.database import (  # noqa
    building_db_model,
    calendar_db_model,
    calendar_holiday_category_link,
    classroom_db_model,
    department_classroom_link,
    department_db_model,
    holiday_category_db_model,
    holiday_db_model,
    subject_building_link,
    subject_db_model,
    user_building_link,
    user_db_model,
)

engine = create_engine(f"{CONFIG.db_uri}/{CONFIG.db_database}")


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
