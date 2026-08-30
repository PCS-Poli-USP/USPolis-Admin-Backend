from server.models.dicts.base.forum_post_base_dict import ForumPostBaseDict
from tests.factories.base.base_factory import BaseFactory


class ForumPostBaseFactory(BaseFactory):
    def __init__(self) -> None:
        super().__init__()

    def get_base_defaults(self) -> ForumPostBaseDict:
        return {
            "content": self.faker.sentence(),
        }
