from server.models.dicts.base.class_base_dict import ClassBaseDict
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.audiovisual_type_enum import AudiovisualType
from server.utils.enums.class_type import ClassType
from tests.factories.base.base_factory import BaseFactory


class ClassBaseFactory(BaseFactory):
    def __init__(self) -> None:
        super().__init__()

    def get_base_defaults(self) -> ClassBaseDict:
        semester = BrazilDatetime.current_semester()
        return {
            "start_date": semester[0].date(),
            "end_date": semester[1].date(),
            "code": self.faker.numerify(text="%%%%%%%"),
            "professors": [self.faker.name()],
            "type": self.faker.random_element(ClassType.values()),
            "vacancies": self.faker.random_int(min=1, max=100),
            "air_conditionating": self.faker.boolean(),
            "accessibility": self.faker.boolean(),
            "audiovisual": self.faker.random_element(AudiovisualType.values()),
            "ignore_to_allocate": self.faker.boolean(),
        }
