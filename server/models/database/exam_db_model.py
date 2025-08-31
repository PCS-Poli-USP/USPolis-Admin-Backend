from sqlmodel import Field, Relationship
from server.models.database.base_db_model import BaseModel
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.exam_class_link import ExamClassLink
from server.models.database.reservation_db_model import Reservation
from server.models.database.schedule_db_model import Schedule
from server.models.database.subject_db_model import Subject


class Exam(BaseModel, table=True):
    reservation_id: int = Field(foreign_key="reservation.id")
    subject_id: int = Field(foreign_key="subject.id")

    reservation: Reservation = Relationship(
        back_populates="exam", sa_relationship_kwargs={"cascade": "delete"}
    )
    subject: Subject = Relationship(back_populates="exams")
    classes: list[Class] = Relationship(
        back_populates="exams", link_model=ExamClassLink
    )

    def get_classroom(self) -> Classroom | None:
        """
        Get the classroom associated with the exam.
        """
        return self.reservation.schedule.classroom

    def get_schedule(self) -> Schedule:
        """
        Get the schedule associated with the exam.
        """
        return self.reservation.schedule
