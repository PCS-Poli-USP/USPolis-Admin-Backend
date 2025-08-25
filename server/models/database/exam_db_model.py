from sqlmodel import Field, Relationship
from server.models.database.base_db_model import BaseModel
from server.models.database.class_db_model import Class
from server.models.database.exam_class_link import ExamClassLink
from server.models.database.reservation_db_model import Reservation
from server.models.database.subject_db_model import Subject


class Exam(BaseModel, table=True):
    reservation_id: int = Field(foreign_key="reservation.id")
    subject_id: int = Field(foreign_key="subject.id")

    reservation: Reservation = Relationship(back_populates="exam")
    subject: Subject = Relationship()
    classes: list[Class] = Relationship(
        back_populates="exams", link_model=ExamClassLink
    )
