from threading import Lock
from src.common.database import database


class SingletonMeta(type):
    _instances = {}

    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class ClassroomsRepository(metaclass=SingletonMeta):
    def __init__(self):
        self.classrooms_collection = database["classrooms"]

    def list_by_building(self, building_name: str):
        return list(self.classrooms_collection.find({"building": building_name}))
