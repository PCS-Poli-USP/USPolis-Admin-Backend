from sqlmodel import Field, SQLModel


class ExamClassLink(SQLModel, table=True):
    exam_id: int | None = Field(
        default=None, foreign_key="exam.id", primary_key=True, ondelete="CASCADE"
    )
    class_id: int | None = Field(
        default=None, foreign_key="class.id", primary_key=True, ondelete="CASCADE"
    )
