from src.repository.classrooms_repository import ClassroomsRepository
from src.repository.events_repository import EventsRepository
from src.services.conflicts.conflict_calculator import ConflictCalculator


def list_available_classrooms(events_ids, building_id, building_name):
    events_repository = EventsRepository()
    classrooms_repository = ClassroomsRepository()

    events_to_be_checked = events_repository.list_by_ids(events_ids)

    classrooms_list = classrooms_repository.list_by_building(building_name)
    grouped_events = events_repository.list_by_building_grouped_by_classroom(
        building_id
    )

    for classroom in classrooms_list:
        classroom["conflicted"] = False

    for event_to_be_checked in events_to_be_checked:
        for classroom, events in grouped_events.items():
            if ConflictCalculator.check_time_conflict_one_with_many(
                event_to_be_checked, events
            ):
                for c in classrooms_list:
                    if c.get("classroom_name") == classroom:
                        c["conflicted"] = True

    return classrooms_list
