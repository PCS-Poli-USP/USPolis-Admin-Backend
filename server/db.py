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
    event_db_model,
    forum_db_model,
    forum_post_reacts_link,
    forum_post_report_link,
    holiday_category_db_model,
    holiday_db_model,
    institutional_event_db_model,
    mobile_comments_db_model,
    mobile_user_db_model,
    occurrence_db_model,
    reservation_db_model,
    schedule_db_model,
    solicitation_db_model,
    subject_building_link,
    subject_db_model,
    user_building_link,
    user_db_model,
    allocation_log_db_model,
    intentional_conflict_db_model,
    exam_db_model,
    meeting_db_model,
    occurrence_label_db_model,
    feedback_db_model,
    bug_report_db_model,
    bug_report_evidence_db_model,
    user_session_db_model,
    course_db_model,
    curriculum_db_model,
    curriculum_subject_db_model
)
engine = create_engine(f"{CONFIG.db_uri}/{CONFIG.db_database}")


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
