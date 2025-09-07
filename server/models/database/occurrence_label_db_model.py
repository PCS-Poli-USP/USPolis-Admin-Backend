from sqlmodel import Field, Relationship
from server.models.database.base_db_model import BaseModel
from server.models.database.occurrence_db_model import Occurrence


class OccurrenceLabel(BaseModel, table=True):
    occurrence_id: int = Field(foreign_key="occurrence.id", unique=True)
    label: str = Field(max_length=50)

    occurrence: Occurrence = Relationship(back_populates="occurrence_label")
