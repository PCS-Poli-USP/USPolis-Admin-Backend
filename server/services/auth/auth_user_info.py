from pydantic import BaseModel


from typing import Any


class AuthUserInfo(BaseModel):
    email: str
    email_verified: bool
    name: str
    picture: str
    given_name: str
    family_name: str

    @staticmethod
    def from_dict(info: dict[str, Any]) -> "AuthUserInfo":
        return AuthUserInfo(
            email=info["email"],
            email_verified=info["email_verified"],
            name=info["name"],
            picture=info["picture"],
            given_name=info["given_name"],
            family_name=info["family_name"],
        )
