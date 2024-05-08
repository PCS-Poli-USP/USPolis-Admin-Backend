from datetime import datetime

from beanie import Document, Link

from server.models.database.classroom_db_model import Classroom
from server.models.database.schedule_db_model import Schedule
from server.models.database.user_db_model import User


class Reservation(Document):
    classroom:Link[Classroom]
    schedule:Link[Schedule]
    name:str
    type:str
    description:str
    created_by:Link[User]
    updated_at:datetime

    class Settings:
        name = "reservations"
