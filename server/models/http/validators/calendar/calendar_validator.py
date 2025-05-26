class CalendarValidator:
    @staticmethod
    def validate_name(name: str) -> bool:
        return len(name) > 0
