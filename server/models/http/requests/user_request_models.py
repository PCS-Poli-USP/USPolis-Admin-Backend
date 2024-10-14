from pydantic import BaseModel, EmailStr, field_validator


class UserUpdate(BaseModel):
    is_admin: bool
    building_ids: list[int] | None = None


class UserRegister(UserUpdate):
    name: str
    username: str
    email: EmailStr

    @field_validator("username")
    @classmethod
    def check_no_spaces(cls, v: str) -> str:
        if " " in v:
            raise ValueError("Username must not contain spaces")
        return v
