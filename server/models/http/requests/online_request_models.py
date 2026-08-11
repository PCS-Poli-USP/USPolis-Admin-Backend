from pydantic import BaseModel


class OnlineClientMessage(BaseModel):
    page: str | None = None
