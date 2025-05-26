from datetime import datetime
from server.models.database.calendar_db_model import Calendar
from server.models.database.forum_db_model import ForumPost
from server.models.database.schedule_db_model import Schedule
from server.models.database.subject_db_model import Subject
from server.models.dicts.base.class_base_dict import ClassBaseDict
from server.models.dicts.database.base_database_dicts import BaseModelDict


class ClassModelDict(ClassBaseDict, BaseModelDict, total=False):
    """
    Class to hold the model dictionary for the database.
    """

    full_allocated: bool
    updated_at: datetime

    # Relationships
    calendars: list[Calendar]
    schedules: list[Schedule]
    subject: Subject
    posts: list[ForumPost]
