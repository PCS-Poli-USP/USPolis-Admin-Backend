from datetime import datetime


class ConflictsUtils:
    @staticmethod
    def check_time_overlap(event1: dict, event2: dict) -> bool:
        start_time1 = ConflictsUtils.parse_event_time(event1.get("start_time"))
        end_time1 = ConflictsUtils.parse_event_time(event1.get("end_time"))
        start_time2 = ConflictsUtils.parse_event_time(event2.get("start_time"))
        end_time2 = ConflictsUtils.parse_event_time(event2.get("end_time"))

        return (
            start_time1 <= start_time2 <= end_time1
            or start_time2 <= start_time1 <= end_time2
            or (start_time1 <= start_time2 and end_time1 >= end_time2)
            or (start_time2 <= start_time1 and end_time2 >= end_time1)
        )

    @staticmethod
    def parse_event_time(time) -> datetime:
        return datetime.strptime(time, "%H:%M")
