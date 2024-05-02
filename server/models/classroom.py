from datetime import datetime

from beanie import Document, Link

from server.models.building import Building
from server.models.user import User


class Classroom(Document):
    building: Link[Building]
    name: str
    capacity: int
    floor: int
    ignore_to_allocate: bool
    accessibility: bool
    projector: bool
    air_conditioning: bool
    created_by: Link[User]
    updated_at: datetime

    class Settings:
        name = "classrooms"
