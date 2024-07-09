from datetime import datetime

from pydantic import BaseModel


class ForumPostRegister(BaseModel):
    class_id : int 
    author : str
    post_title : str | None = None
    content : str | None = None