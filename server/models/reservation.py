from beanie import Document, Link
from datetime import datetime

from database.models.schedule import Schedule
from database.models.classroom import Classroom
from database.models.user_building import User


class Reservation(Document):
    classroom = Link[Classroom]
    schedule = Link[Schedule]
    name = str
    type = str
    description = str
    created_by = Link[User]
    updated_at = datetime

    class Settings:
        name = "reservations"
