from beanie import Document, Link
from datetime import datetime

from database.models.user_building import Building, User


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
