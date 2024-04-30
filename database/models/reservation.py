from beanie import Document, Link
from datetime import datetime

from schedule import Schedule
from classroom import Classroom
from user import User


class Reservation(Document):
    classroom = Link[Classroom]
    schedule = Link[Schedule]
    name = str
    type = str
    description = str
    created_by = Link[User]
    updated_at = datetime

    class Settings:
        name = 'reservations'
