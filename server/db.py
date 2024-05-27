from collections.abc import Generator

from sqlmodel import Session, create_engine

from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User
from server.models.database.holiday_category_db_model import HolidayCategory
from server.models.database.holiday_db_model import Holiday

from server.config import CONFIG

engine = create_engine(f"{CONFIG.db_uri}/{CONFIG.db_database}")


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
