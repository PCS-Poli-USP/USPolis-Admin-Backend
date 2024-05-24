from fastapi import Response, status
from pydantic import BaseModel


class Message(BaseModel):
    message: str

    @classmethod
    def from_message(cls, message: str) -> "Message":
        return cls(message=message)


NoContent = Response(status_code=status.HTTP_204_NO_CONTENT)
