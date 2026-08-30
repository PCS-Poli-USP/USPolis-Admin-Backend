from server.models.dicts.base.mobile_user_base_dict import MobileUserBaseDict
from tests.factories.base.base_factory import BaseFactory


class MobileUserBaseFactory(BaseFactory):
    def __init__(self) -> None:
        super().__init__()

    def get_base_defaults(self) -> MobileUserBaseDict:
        return {
            "sub": self.faker.unique.uuid4(),
            "email": self.faker.email(domain="usp.br"),
            "given_name": self.faker.first_name(),
            "family_name": self.faker.last_name(),
            "picture_url": None,
        }
