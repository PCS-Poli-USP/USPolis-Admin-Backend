from pydantic import BaseModel, EmailStr


class UserUpdate(BaseModel):
    is_admin: bool
    building_ids: list[int] | None = None


class UserRegister(UserUpdate):
    name: str
    email: EmailStr
