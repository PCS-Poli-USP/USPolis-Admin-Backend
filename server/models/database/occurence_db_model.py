from beanie import Document, Link
from datetime import datetime

from server.models.database.classroom_db_model import Classroom
from server.models.database.schedule_db_model import Schedule


class Ocurrence(Document):
    classroom = Link[Classroom]
    schedule = Link[Schedule]
    start_time = str
    end_time = str
    date = datetime

    class Settings:
        name = "occurrences"
