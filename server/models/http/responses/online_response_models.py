from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class OnlineConnectionResponse(BaseModel):
    connection_id: str
    user_id: int | None
    name: str | None
    email: str | None
    ip_address: str
    user_agent: str
    connected_since: datetime
    page: str | None


class OnlineSnapshotEvent(BaseModel):
    event: Literal["snapshot"] = "snapshot"
    connections: list[OnlineConnectionResponse]


class OnlineDiffEvent(BaseModel):
    event: Literal["diff"] = "diff"
    upserted: list[OnlineConnectionResponse]
    removed: list[str]
