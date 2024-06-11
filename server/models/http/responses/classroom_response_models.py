from pydantic import BaseModel

from server.models.database.classroom_db_model import Classroom


class ClassroomResponse(BaseModel):
    @classmethod
    def from_classroom(cls, classroom: Classroom) -> "ClassroomResponse":
        return cls()

    @classmethod
    def from_classroom_list(
        cls, classrooms: list[Classroom]
    ) -> list["ClassroomResponse"]:
        return [cls.from_classroom(classroom) for classroom in classrooms]
