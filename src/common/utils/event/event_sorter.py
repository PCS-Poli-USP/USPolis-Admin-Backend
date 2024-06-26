from src.common.utils.days import days_index, reverse_days_index
    
def sort_events_by_subscribers(event: dict):
  return event['subscribers']

def sort_events_by_vacancies(event: dict):
  return event["vacancies"]

def sort_events_by_subject_code(event: dict):
  return event["subject_code"]

def sort_events_by_time(event: dict):
  return (days_index(event["week_day"]), event["start_time"])

def sort_events_by_class(event: dict):
  return (event["vacancies"], event["subject_code"])

def sort_events_by_class_and_time(event: dict):
  return (event["vacancies"], event["subject_code"], reverse_days_index(event["week_day"]), event["start_time"])