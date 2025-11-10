from enum import StrEnum


class BugPriority(StrEnum):
    LOW = "low"
    AVERAGE = "average"
    HIGH = "high"
    URGENT = "urgent"

    @staticmethod
    def values() -> list["BugPriority"]:
        return [
            BugPriority.LOW,
            BugPriority.AVERAGE,
            BugPriority.HIGH,
            BugPriority.URGENT,
        ]

    @staticmethod
    def to_ptBr(value: "BugPriority") -> str:
        match value:
            case BugPriority.LOW:
                return "Baixa"
            case BugPriority.AVERAGE:
                return "Média"
            case BugPriority.HIGH:
                return "Alta"
            case BugPriority.URGENT:
                return "Urgente"
            case _:
                return "Desconhecido"


class BugType(StrEnum):
    FUNCTIONALITY = "functionality"
    PERFORMANCE = "performance"
    SECURITY = "security"
    CRASH_ERROR = "crash_error"
    UI = "ui"
    OTHER = "other"

    @staticmethod
    def values() -> list["BugType"]:
        return [
            BugType.FUNCTIONALITY,
            BugType.PERFORMANCE,
            BugType.SECURITY,
            BugType.CRASH_ERROR,
            BugType.UI,
            BugType.OTHER,
        ]


class BugStatus(StrEnum):
    PENDING = "pending"
    RESOLVED = "resolved"
    IN_PROGRESS = "in_progress"
    SKIPPED = "skipped"

    @staticmethod
    def values() -> list["BugStatus"]:
        return [
            BugStatus.PENDING,
            BugStatus.RESOLVED,
            BugStatus.IN_PROGRESS,
            BugStatus.SKIPPED,
        ]
