from datetime import date, datetime
from server.models.database.calendar_db_model import Calendar
from server.models.database.forum_db_model import ForumPost
from server.models.database.schedule_db_model import Schedule
from server.models.database.subject_db_model import Subject
from server.models.dicts.database.base_database_dicts import BaseModelDict
from server.utils.enums.audiovisual_type_enum import AudiovisualType
from server.utils.enums.class_type import ClassType


class ClassModelDict(BaseModelDict):
    """
    Class to hold the model dictionary for the database.
    """

    start_date: date
    end_date: date
    code: str
    professors: list[str]
    type: ClassType
    vacancies: int

    air_conditionating: bool
    accessibility: bool
    audiovisual: AudiovisualType
    ignore_to_allocate: bool
    full_allocated: bool
    updated_at: datetime

    # Relationships
    calendars: list[Calendar]
    schedules: list[Schedule]
    subject: Subject
    posts: list[ForumPost]
