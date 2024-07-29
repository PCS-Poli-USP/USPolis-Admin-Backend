from sqlmodel import Field, SQLModel


class MobileUser(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    sub: str = Field() # The unique ID of the user's Google Account
    email: str = Field()
    given_name: str = Field()
    family_name: str = Field()
    picture_url: str | None = Field(default=None)
