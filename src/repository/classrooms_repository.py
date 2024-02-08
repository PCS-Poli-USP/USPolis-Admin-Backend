from src.common.database import database
from src.common.singleton_meta import SingletonMeta


class ClassroomsRepository(metaclass=SingletonMeta):
    def __init__(self):
        self.classrooms_collection = database["classrooms"]

    def list_by_building(self, building_name: str):
        return list(self.classrooms_collection.find({"building": building_name}))
