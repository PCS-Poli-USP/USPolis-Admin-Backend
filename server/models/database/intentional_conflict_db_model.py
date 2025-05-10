from sqlalchemy import UniqueConstraint
from sqlmodel import Field

from server.models.database.base_db_model import BaseModel


class IntentionalConflict(BaseModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "fist_occurrence_id",
            "second_occurrence_id",
            name="unique_occurrence_pair",
        ),
    )

    fist_occurrence_id: int = Field(foreign_key="occurrence.id")
    second_occurrence_id: int = Field(foreign_key="occurrence.id")
