from server.models.dicts.base.curriculum_base_dict import CurriculumBaseDict
from tests.factories.base.base_factory import BaseFactory


class CurriculumBaseFactory(BaseFactory):
    def __init__(self) -> None:
        super().__init__()

    def get_base_defaults(self) -> CurriculumBaseDict:
        return {
            "codcur": self.faker.unique.random_int(min=1, max=99),
            "codhab": self.faker.random_int(min=1, max=999),
            "AAC": self.faker.random_int(min=0, max=20),
            "AEX": self.faker.random_int(min=0, max=20),
            "description": self.faker.unique.sentence(nb_words=3),
        }
