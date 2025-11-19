from server.models.dicts.base.feedback_base_dict import FeedbackBaseDict
from tests.factories.base.base_factory import BaseFactory


class FeedbackBaseFactory(BaseFactory):
    def __init__(self) -> None:
        super().__init__()

    def get_base_defaults(self) -> FeedbackBaseDict:
        return {"title": self.faker.sentence(), "message": self.faker.text()}
