from datetime import datetime

from src.common.database import database

events_collection = database["events"]

from src.common.utils.classes.classes_mapper import get_class_schedule
from src.common.utils.classroom.classroom_mapper import get_classroom_schedule
from src.common.utils.event.event_mapper import get_events_by_class
from src.common.utils.classes.classes_sorter import sort_classes_by_vacancies
from src.common.utils.classroom.classroom_sorter import sort_classrooms_by_capacity
from src.common.utils.event.event_sorter import sort_events_by_class, sort_events_by_vacancies, sort_events_by_subject_code, sort_events_by_time, sort_events_by_class_and_time

def classroom_capacity_validation(classroom: dict, event: dict) -> bool:
  return classroom["capacity"] >= event["vacancies"]

def classroom_preferences_validation(classroom: dict, preferences: dict) -> bool:
    return preferences["projector"] == classroom["projector"] and \
           preferences["air_conditioning"] == classroom["air_conditioning"] and \
           preferences["accessibility"] == classroom["accessibility"]

def classroom_times_validation(classroom: dict, classroom_schedule, event: dict) -> bool:
  start_validation = datetime.strptime(event["start_time"], "%H:%M").time()
  end_validation = datetime.strptime(event["end_time"], "%H:%M").time()
  classroom_times = classroom_schedule[event["week_day"]]
  for classroom_time in classroom_times:
    start = datetime.strptime(classroom_time[0], "%H:%M").time()
    end = datetime.strptime(classroom_time[1], "%H:%M").time()
    if (start_validation < start and end_validation < end):
      return False
    if (start_validation > start and end_validation < end):
      return False
    if (start_validation < end and end_validation > end):
      return False
    if (start_validation < start and end_validation > end):
      return False
  return True

def classroom_is_allowed_to_allocate(classroom: dict, classroom_schedule, event: dict) -> bool:
  if classroom_capacity_validation(classroom, event):
    if classroom_times_validation(classroom, classroom_schedule, event):
      return True    
  return False

def allocate_classrooms(classroom_list: list, event_list: list):
  classroom_list.sort(key=sort_classrooms_by_capacity, reverse=True)
  event_list.sort(key=sort_events_by_class_and_time, reverse=True)

  events_by_class = get_events_by_class(event_list)
  allocated_events = []
  unallocated_events = []

  for (subject_code, class_code), events in events_by_class.items():
      partial_allocated = []
      for event in events:
        for classroom in classroom_list:
            classroom_schedule = get_classroom_schedule(classroom)
            if classroom_is_allowed_to_allocate(classroom, classroom_schedule, event):
                print("Turma: ", event["subject_code"], event["class_code"], event['week_day'], event['start_time'], "allocada em", classroom["classroom_name"])
                event["has_to_be_allocated"] = False
                event["classroom"] = classroom["classroom_name"]
                event["building"] = classroom["building"]
                partial_allocated.append(event)
                break
      if len(partial_allocated) != len(events):
        difference = len(events) - len(partial_allocated)
        print("Não foi possível alocar", subject_code, class_code, "tivemos", difference, "horários não alocados")
        unallocated_events.extend(events)
      else:
        for event in partial_allocated:
          filter = {"subject_code" : subject_code, "class_code" : class_code, "week_day": event["week_day"], "start_time" : event["start_time"]}
          query = {"$set": {"has_to_be_allocated" : False, "classroom" : event["classroom"], "building" : event["building"]}}
          events_collection.update_one(filter, query)
          allocated_events.append(event)

  return (allocated_events, unallocated_events)