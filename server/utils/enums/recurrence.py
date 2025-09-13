from enum import Enum


class Recurrence(str, Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    BIWEEKLY = "Biweekly"
    MONTHLY = "Monthly"
    CUSTOM = "Custom"

    def to_string(self) -> str:
        return self.value

    def translated(self) -> str:
        translations = {
            Recurrence.DAILY: "Diário",
            Recurrence.WEEKLY: "Semanal",
            Recurrence.BIWEEKLY: "Quinzenal",
            Recurrence.MONTHLY: "Mensal",
            Recurrence.CUSTOM: "Personalizado",
        }
        return translations.get(self, "Desconhecido")

    @staticmethod
    def values() -> list["Recurrence"]:
        return [
            Recurrence.DAILY,
            Recurrence.WEEKLY,
            Recurrence.BIWEEKLY,
            Recurrence.MONTHLY,
            Recurrence.CUSTOM,
        ]
