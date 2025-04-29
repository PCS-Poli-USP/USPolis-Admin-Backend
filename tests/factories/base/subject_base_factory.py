from server.models.dicts.base.subject_base_dict import SubjectBaseDict
from server.utils.enums.subject_type import SubjectType
from tests.factories.base.base_factory import BaseFactory


class SubjectBaseFactory(BaseFactory):
    def __init__(self) -> None:
        super().__init__()

    def get_base_defaults(self) -> SubjectBaseDict:
        return {
            "name": self.faker.name(),
            "code": self.faker.bothify(text="??###", letters=self.UPPER_LETTERS),
            "professors": [self.faker.name() for _ in range(3)],
            "type": self.faker.random_element(SubjectType.values()),
            "class_credit": self.faker.random_int(min=1, max=10),
            "work_credit": self.faker.random_int(min=1, max=10),
        }
