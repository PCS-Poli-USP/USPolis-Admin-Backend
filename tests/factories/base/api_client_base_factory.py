from server.models.dicts.base.api_client_base_dict import ApiClientBaseDict
from tests.factories.base.base_factory import BaseFactory


class ApiClientBaseFactory(BaseFactory):
    """Base factory for API client model or request."""

    def get_base_defaults(self) -> ApiClientBaseDict:
        return {
            "name": self.faker.unique.company(),
            "organization": self.faker.company(),
            "contact_name": self.faker.name(),
            "contact_email": self.faker.email(),
            "description": self.faker.sentence(),
        }
