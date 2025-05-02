from server.models.dicts.base.classroom_base_dict import ClassroomBaseDict
from server.utils.enums.audiovisual_type_enum import AudiovisualType
from tests.factories.base.base_factory import BaseFactory


class ClassroomBaseFactory(BaseFactory):
    def __init__(self) -> None:
        super().__init__()

    def get_base_defaults(self) -> ClassroomBaseDict:
        return {
            "name": self.faker.cryptocurrency_name(),
            "capacity": self.faker.random_int(min=0, max=100),
            "floor": self.faker.random_int(min=0, max=10),
            "accessibility": self.faker.boolean(),
            "audiovisual": self.faker.random_element(AudiovisualType.values()),
            "air_conditioning": self.faker.boolean(),
        }
