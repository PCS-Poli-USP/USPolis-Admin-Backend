from server.models.database.classroom_db_model import Classroom
from server.models.database.occurrence_label_db_model import OccurrenceLabel
from server.models.database.schedule_db_model import Schedule
from server.models.dicts.base.occurrence_base_dict import OccurrenceBaseDict
from server.models.dicts.database.base_database_dicts import BaseModelDict


class OccurrenceModelDict(BaseModelDict, OccurrenceBaseDict, total=False):
    """Class to hold the model dictionary for the database."""

    classroom_id: int | None
    schedule_id: int

    # Relationships
    classroom: Classroom | None
    schedule: Schedule
    occurrence_label: OccurrenceLabel | None
