from datetime import datetime

from pydantic import BaseModel


class ForumPostRegister(BaseModel):
    event_id : int 
    author : str
    content : str | None = None