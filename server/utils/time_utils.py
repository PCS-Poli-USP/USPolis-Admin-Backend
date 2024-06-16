from datetime import time

import pytz

br_tz = pytz.timezone("America/Sao_Paulo")


class TimeUtils:
    @staticmethod
    def time_from_string(time_str: str) -> time:
        time_obj = time.fromisoformat(time_str)
        time_obj_with_tz = time_obj.replace(tzinfo=br_tz)
        return time_obj_with_tz
