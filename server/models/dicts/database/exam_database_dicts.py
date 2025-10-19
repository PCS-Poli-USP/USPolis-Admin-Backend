from server.models.database.class_db_model import Class
from server.models.database.reservation_db_model import Reservation
from server.models.database.subject_db_model import Subject
from server.models.dicts.base.exam_base_dict import ExamBaseDict
from server.models.dicts.database.base_database_dicts import BaseModelDict


class ExamModelDict(ExamBaseDict, BaseModelDict, total=False):
    """TypedDict for Exam database model.\n
    This TypedDict is used to define the structure of the Exam data.\n
    """

    reservation_id: int

    reservation: Reservation
    subject: Subject
    classes: list[Class]
