from collections.abc import Generator

from sqlmodel import Session, create_engine

from server.config import CONFIG

# imports needed for the engine know the models
# add imports for any new model here
from server.models.database import (  # noqa
    building_db_model,
    calendar_db_model,
    calendar_holiday_category_link,
    class_calendar_link,
    class_db_model,
    classroom_db_model,
    forum_db_model,
    holiday_category_db_model,
    holiday_db_model,
    institutional_event_db_model,
    mobile_comments_db_model,
    mobile_user_db_model,
    occurrence_db_model,
    reservation_db_model,
    schedule_db_model,
    subject_building_link,
    subject_db_model,
    user_building_link,
    user_db_model,
    classroom_solicitation_db_model
)

engine = create_engine(f"{CONFIG.db_uri}/{CONFIG.db_database}")


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
