from src.common.database import database
from src.common.utils.event import event_sorter


events_collection = database["events"]

def get_classroom_schedule(classroom: dict) -> list:
  schedule = {
    "seg" : [],
    "ter" : [],
    "qua": [],
    "qui" : [],
    "sex" : [],
    "sab" : [],
    "dom" : [],
  }
  events = list(events_collection.find({"classroom" : classroom["classroom_name"]}))
  events.sort(key=event_sorter.sort_events_by_time)
  for event in events:
    schedule[event["week_day"]].append((event["start_time"], event["end_time"]))
  return schedule