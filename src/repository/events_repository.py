from bson.objectid import ObjectId

from src.common.database import database
from src.common.singleton_meta import SingletonMeta


class EventsRepository(metaclass=SingletonMeta):
    def __init__(self):
        self.__events_tb = database["events"]

    def list_by_building_grouped_by_classroom(
        self, building_id
    ) -> dict[str, list[dict]]:
        query = {"preferences.building_id": ObjectId(building_id)}
        events = list(self.__events_tb.find(query))

        grouped_events = {}
        for event in events:
            classroom = event.get("classroom")
            if classroom is None:
                continue
            if classroom not in grouped_events:
                grouped_events[classroom] = []
            grouped_events[classroom].append(event)

        return grouped_events
