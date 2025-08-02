from pydantic import BaseModel, EmailStr


class UserUpdate(BaseModel):
    is_admin: bool
    group_ids: list[int] = []
    receive_emails: bool = True


class UserRegister(UserUpdate):
    name: str
    email: EmailStr
