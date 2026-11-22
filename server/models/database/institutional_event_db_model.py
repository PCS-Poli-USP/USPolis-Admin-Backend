from datetime import datetime

from sqlmodel import Field

from server.models.database.base_db_model import BaseModel
from server.utils.brazil_datetime import BrazilDatetime


class InstitutionalEvent(BaseModel, table=True):
    title: str = Field()
    description: str = Field()
    category: str = Field()
    start: datetime = Field()
    end: datetime = Field()
    location: str | None = Field()
    building: str | None = Field()
    classroom: str | None = Field()
    external_link: str | None = Field()
    likes: int = Field(default=0)
    created_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    # Who created the event: only them or an admin edits or deletes it (same
    # rule as holidays and calendars). NULL for events created before it was
    # recorded, which only admins can change.
    created_by_id: int | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL"
    )
