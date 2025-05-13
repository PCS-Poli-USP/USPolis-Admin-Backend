from sqlalchemy import UniqueConstraint
from sqlmodel import Field

from server.models.database.base_db_model import BaseModel


class IntentionalConflict(BaseModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "first_occurrence_id",
            "second_occurrence_id",
            name="unique_occurrence_pair",
        ),
    )

    first_occurrence_id: int = Field(foreign_key="occurrence.id", ondelete="CASCADE")
    second_occurrence_id: int = Field(foreign_key="occurrence.id", ondelete="CASCADE")
