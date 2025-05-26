from sqlmodel import Field

from server.models.database.base_db_model import BaseModel


class MobileUser(BaseModel, table=True):
    sub: str = Field()  # The unique ID of the user's Google Account
    email: str = Field()
    given_name: str = Field()
    family_name: str = Field()
    picture_url: str | None = Field(default=None)
