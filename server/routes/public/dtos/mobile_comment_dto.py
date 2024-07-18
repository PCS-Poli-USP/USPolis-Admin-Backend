from datetime import datetime
from pydantic import BaseModel


class MobileCommentRegister(BaseModel):
    comment: str
    email: str | None

class MobileCommentResponse(MobileCommentRegister):
    created_at: datetime