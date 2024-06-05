from datetime import datetime

from sqlmodel import Field, SQLModel


class InstitutionalEvent(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    title: str = Field()
    description: str = Field(nullable=False)
    start: datetime = Field()
    end: datetime | None = Field()
    location: str = Field()
    external_link: str = Field()
    likes: int = Field()
    category: str = Field()
    created_at: datetime = Field(default=datetime.now())
    building: str = Field()
