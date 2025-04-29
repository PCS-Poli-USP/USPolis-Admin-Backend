from datetime import date, timedelta
from server.models.dicts.base.class_base_dict import ClassBaseDict
from server.utils.enums.audiovisual_type_enum import AudiovisualType
from server.utils.enums.class_type import ClassType
from tests.factories.base.base_factory import BaseFactory


class ClassBaseFactory(BaseFactory):
    def __init__(self) -> None:
        super().__init__()

    def get_base_defaults(self) -> ClassBaseDict:
        return {
            "start_date": date.today(),
            "end_date": date.today() + timedelta(days=30),
            "code": self.faker.numerify(text="%%%%%%%"),
            "professors": [self.faker.name()],
            "type": self.faker.random_element(ClassType.values()),
            "vacancies": self.faker.random_int(min=1, max=100),
            "air_conditionating": self.faker.boolean(),
            "accessibility": self.faker.boolean(),
            "audiovisual": self.faker.random_element(AudiovisualType.values()),
            "ignore_to_allocate": self.faker.boolean(),
        }
