from datetime import datetime

from src.common.database import database

events = database["events"]

from src.common.utils.classes.classes_mapper import get_class_schedule
from src.common.utils.classroom.classroom_mapper import get_classroom_schedule
from src.common.utils.classes.classes_sorter import sort_classes_by_vacancies
from src.common.utils.classroom.classroom_sorter import sort_classrooms_by_capacity
from src.common.utils.event.event_sorter import sort_events_by_class

def classroom_capacity_validation(classroom: dict, _class: dict) -> bool:
  return classroom["capacity"] >= _class["vacancies"]

def classroom_preferences_validation(classroom: dict, preferences: dict) -> bool:
    return preferences["projector"] == classroom["projector"] and \
           preferences["air_conditioning"] == classroom["air_conditioning"] and \
           preferences["accessibility"] == classroom["accessibility"]

def classroom_times_validation(classroom: dict, _class: dict) -> bool:
  classroom_schedule = get_classroom_schedule(classroom)
  class_schedule = get_class_schedule(_class)

  for day, times in class_schedule.items():
    for time in times:
      start_validation = datetime.strptime(time[0], "%H:%M").time()
      end_validation = datetime.strptime(time[1], "%H:%M").time()
      classroom_times = classroom_schedule[day]
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

def classroom_is_allowed_to_allocate(classroom: dict, _class: dict) -> bool:
  if classroom_capacity_validation(classroom, _class):
    if classroom_times_validation(classroom, _class):
      return True    
  return False

def allocate_classrooms(classroom_list: list, class_list: list):
  classroom_list.sort(key=sort_classrooms_by_capacity, reverse=True)
  class_list.sort(key=sort_classes_by_vacancies, reverse=True)

  allocated_classes = []
  unallocated_classes = []

  for _class in class_list:
      allocated = False
      for classroom in classroom_list:
          if classroom_is_allowed_to_allocate(classroom, _class):
              print("Turma: ", _class["subject_code"], _class["class_code"], "allocada em", classroom["classroom_name"])
              filter = {"subject_code" : _class["subject_code"], "class_code" : _class["class_code"]}
              query = {"$set": {"has_to_be_allocated" : False, "classroom" : classroom["classroom_name"], "building" : classroom["building"]}}
              events.update_many(filter, query)
              _class["has_to_be_allocated"] = False
              _class["classrooms"] = [classroom["classroom_name"]]
              _class["building"] = classroom["building"]
              allocated_classes.append(_class)
              allocated = True
              break
      if not allocated:
          print("Não foi possível alocar", _class["subject_code"], _class["class_code"])
          unallocated_classes.append(_class)

  return (allocated_classes, unallocated_classes)