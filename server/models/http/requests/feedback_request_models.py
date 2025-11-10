from typing import Self
from fastapi import HTTPException, status
from pydantic import BaseModel, model_validator


class FeedbackRegister(BaseModel):
    title: str
    message: str

    @model_validator(mode="after")
    def validate_body(self) -> Self:
        if len(self.title) == 0:
            raise FeedbackInvalidInput("Deve-se fornecer um título")
        if len(self.message) == 0:
            raise FeedbackInvalidInput("Deve-se fornecer uma mensagem")
        return self


class FeedbackInvalidInput(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
