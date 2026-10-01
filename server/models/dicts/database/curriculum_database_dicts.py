from datetime import datetime

from server.models.database.course_db_model import Course
from server.models.database.curriculum_subject_db_model import CurriculumSubject
from server.models.database.user_db_model import User
from server.models.dicts.base.curriculum_base_dict import CurriculumBaseDict
from server.models.dicts.database.base_database_dicts import BaseModelDict


class CurriculumModelDict(BaseModelDict, CurriculumBaseDict, total=False):
    """Class to hold the model dictionary for the database."""

    course_id: int
    created_at: datetime
    created_by_id: int
    updated_at: datetime
    updated_by_id: int

    # Relationships
    course: Course
    subjects: list[CurriculumSubject]
    users: list[User]
