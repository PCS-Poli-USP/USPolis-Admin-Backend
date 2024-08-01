from typing import Self
from pydantic import BaseModel

from server.models.database.mobile_user_db_model import MobileUser
from server.utils.must_be_int import must_be_int


class AuthenticatedUser(BaseModel):
    id: int
    sub: str
    given_name: str
    family_name: str
    email: str
    picture_url: str

    @classmethod
    def from_model(cls, user: MobileUser | None) -> Self | None:
        if user is not None:
            return cls(
                id=must_be_int(user.id),
                sub=user.sub,
                given_name=user.given_name,
                family_name=user.family_name,
                email=user.email,
                picture_url=user.picture_url if user.picture_url else "",
            )
        else:
            return None


class AuthenticationResponse(BaseModel):
    is_registered_user: bool
    user: AuthenticatedUser | None

    @classmethod
    def from_model_user(cls, modelUser: MobileUser | None) -> "AuthenticationResponse":
        authUser = AuthenticatedUser.from_model(modelUser)
        if authUser is not None:
            is_registered_user = True
        else:
            is_registered_user = False
        return cls(is_registered_user=is_registered_user, user=authUser)
