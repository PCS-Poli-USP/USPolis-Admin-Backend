from pydantic import BaseModel


from typing import Any


class AuthUserInfo(BaseModel):
    email: str
    email_verified: bool
    domain: str
    name: str
    picture: str
    given_name: str
    family_name: str

    @staticmethod
    def from_dict(info: dict[str, Any]) -> "AuthUserInfo":
        email: str = info["email"]
        domain = email.split("@")[1]
        return AuthUserInfo(
            email=info["email"],
            email_verified=info["email_verified"],
            domain=domain,
            name=info["name"],
            picture=info["picture"],
            given_name=info["given_name"],
            family_name=info.get("family_name", ""),
        )

    @staticmethod
    def monitor_auth_info() -> "AuthUserInfo":
        return AuthUserInfo(
            email="uspolis@usp.br",
            email_verified=True,
            picture="https://lh3.googleusercontent.com/a/ACg8ocJqVUye4OtOD_elvMw-AqIsLsAjiCbluauxKF2Hk2zxvAwKsA=s288-c-mo-no",
            domain="usp.br",
            name="USPolis Monitor",
            given_name="USPolis",
            family_name="Monitor",
        )
