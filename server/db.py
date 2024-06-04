from collections.abc import Generator

from sqlmodel import Session, create_engine

import server.models.database.classroom_db_model  # noqa
from server.config import CONFIG
from server.models.database.building_db_model import Building  # noqa
from server.models.database.holiday_category_db_model import HolidayCategory  # noqa
from server.models.database.holiday_db_model import Holiday  # noqa
from server.models.database.user_db_model import User  # noqa

engine = create_engine(f"{CONFIG.db_uri}/{CONFIG.db_database}")


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
