def get_class_schedule(_class):
  schedule = {
    "seg" : [],
    "ter" : [],
    "qua": [],
    "qui" : [],
    "sex" : [],
    "sab" : [],
    "dom" : [],
  }
  for i in range(0, len(_class["week_days"])):
    schedule[_class["week_days"][i]].append((_class["start_time"][i], _class["end_time"][i]))
  return schedule