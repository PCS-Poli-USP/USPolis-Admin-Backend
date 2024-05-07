
class UserDefaultValues:
    USERNAME = "default username"
    NAME = "default name"
    EMAIL = "default@default.com"
    IS_ADMIN = False
    COGNITO_ID = "default-cognito-id"


class AdminUserDefaultValues(UserDefaultValues):
    USERNAME = "Default admin name"
    IS_ADMIN = True
