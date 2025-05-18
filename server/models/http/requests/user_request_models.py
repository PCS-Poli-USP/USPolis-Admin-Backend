from pydantic import BaseModel, EmailStr


class UserUpdate(BaseModel):
    is_admin: bool
    group_ids: list[int] = []


class UserRegister(UserUpdate):
    name: str
    email: EmailStr
