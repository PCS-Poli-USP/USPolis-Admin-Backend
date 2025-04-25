from datetime import datetime

from sqlmodel import Field, SQLModel


class InstitutionalEvent(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
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
    created_at: datetime = Field(default_factory=datetime.now)
