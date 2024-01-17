def get_events_by_class(event_list: list) -> dict:
  event_by_class = {}
  for event in event_list:
    key = (event["subject_code"], event["class_code"])
    if key not in event_by_class:
      event_by_class[key] = []
    event_by_class[key].append(event)
  return event_by_class