from server.models.database.building_db_model import Building
from server.models.dicts.requests.classroom_requests_dicts import (
    ClassroomRegisterDict,
    ClassroomUpdateDict,
)
from server.models.http.requests.classroom_request_models import (
    ClassroomRegister,
    ClassroomUpdate,
)
from server.utils.must_be_int import must_be_int
from tests.factories.request.base_request_factory import BaseRequestFactory


class ClassroomRequestFactory(BaseRequestFactory):
    def __init__(self, building: Building) -> None:
        super().__init__()
        self.building = building

    def get_default_register_input(self) -> ClassroomRegisterDict:
        """Get default values for creating a ClassroomRegister."""
        return {
            "building_id": must_be_int(self.building.id),
            "name": self.faker.cryptocurrency_name(),
            "capacity": self.faker.random_int(min=0, max=100),
            "floor": self.faker.random_int(min=0, max=10),
            "ignore_to_allocate": self.faker.boolean(),
            "accessibility": self.faker.boolean(),
            "projector": self.faker.boolean(),
            "air_conditioning": self.faker.boolean(),
        }

    def get_default_update_input(self) -> ClassroomUpdateDict:
        return self.get_default_register_input()

    def create_input(self, **overrides: ClassroomRegisterDict) -> ClassroomRegister:
        default = self.get_default_register_input()
        self.update_default_dict(default, overrides)  # type: ignore
        return ClassroomRegister(**default)

    def update_input(self, **overrides: ClassroomUpdateDict) -> ClassroomUpdate:
        default = self.get_default_register_input()
        self.update_default_dict(default, overrides)  # type: ignore
        return ClassroomUpdate(**default)
