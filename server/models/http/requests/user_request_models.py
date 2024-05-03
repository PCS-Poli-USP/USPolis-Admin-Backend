
from pydantic import BaseModel, EmailStr, field_validator


class UserUpdate(BaseModel):
    name: str
    is_admin: bool
    buildings: list[str] | None = None


class UserRegister(UserUpdate):
    username: str
    email: EmailStr

    @field_validator("username")
    @classmethod
    def check_no_spaces(cls, v: str) -> str:
        if " " in v:
            raise ValueError("Username must not contain spaces")
        return v