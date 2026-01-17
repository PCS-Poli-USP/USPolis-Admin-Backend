from enum import StrEnum


class ClassroomPermissionType(StrEnum):
    VIEW = "view"
    RESERVE = "reserve"

    @classmethod
    def to_ptBR(cls, value: "ClassroomPermissionType") -> str:
        match value:
            case ClassroomPermissionType.VIEW:
                return "Visualizar"
            case ClassroomPermissionType.RESERVE:
                return "Reservar"
            case _:
                return "Desconhecido"
