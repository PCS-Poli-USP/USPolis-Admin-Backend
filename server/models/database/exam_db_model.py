from sqlmodel import Field, Relationship
from server.models.database.base_db_model import BaseModel
from server.models.database.class_db_model import Class
from server.models.database.reservation_db_model import Reservation
from server.models.database.subject_db_model import Subject


class Exam(BaseModel, table=True):
    reservation_id: int = Field(foreign_key="reservation.id")
    subject_id: int = Field(foreign_key="subject.id")
    class_id: int = Field(foreign_key="class.id")

    reservation: Reservation = Relationship(back_populates="exam")
    subject: Subject = Relationship()
    class_: Class = Relationship(back_populates="exams")
