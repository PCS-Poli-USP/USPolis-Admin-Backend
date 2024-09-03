from datetime import time
from sqlmodel import Field, SQLModel


class ClassroomSolicitation(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    email: str
    classroom: str
    start_time: time
    end_time: time
    capacity: int
    approved: bool = Field(default=False)
    denied: bool = Field(default=False)
    closed: bool = Field(default=False)
