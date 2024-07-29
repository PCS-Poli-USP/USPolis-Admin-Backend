from pydantic import BaseModel

from server.models.database.mobile_user_db_model import MobileUser

class AuthenticatedUser(BaseModel):
    id: int
    sub: str
    given_name: str
    family_name: str
    email: str
    picture_url: str

    @classmethod
    def from_model(self, user: MobileUser | None) -> "AuthenticatedUser":
        if user != None:
            return self(
                id=user.id,
                sub=user.sub,
                given_name=user.given_name,
                family_name=user.family_name,
                email=user.email,
                picture_url=user.picture_url
                )
        else :
            return None

class AuthenticationResponse(BaseModel):
    is_registered_user: bool
    user: AuthenticatedUser

    @classmethod
    def from_model_user(res, modelUser: MobileUser | None) -> "AuthenticationResponse":
        authUser = AuthenticatedUser.from_model(modelUser)
        if authUser != None:
            is_registered_user = True
        else:
            is_registered_user = False
        res.user = authUser
        return res(
            is_registered_user=is_registered_user,
            user=authUser
        )

