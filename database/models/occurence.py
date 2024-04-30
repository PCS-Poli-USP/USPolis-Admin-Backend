from beanie import Document, Link

from database.models.classroom import Classroom
from database.models.schedule import Schedule


class Ocurrence(Document):
    classroom = Link[Classroom]
    schedule = Link[Schedule]
    start_time = str
    end_time = str
