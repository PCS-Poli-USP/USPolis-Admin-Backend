from datetime import datetime

from beanie import Document, Link

from server.models.database.classroom_db_model import Classroom
from server.models.database.schedule_db_model import Schedule
from server.utils.day_time import DayTime


class Ocurrence(Document):
    classroom = Link[Classroom]
    schedule = Link[Schedule]
    start_time = DayTime
    end_time = DayTime
    date = datetime

    class Settings:
        name = "occurrences"
