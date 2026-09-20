from enum import StrEnum


class BaseAction(StrEnum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"


class BuildingAction(StrEnum):
    CREATE = BaseAction.CREATE
    READ = BaseAction.READ
    UPDATE = BaseAction.UPDATE
    DELETE = BaseAction.DELETE
    ALLOCATE = "allocate"
    RESERVE = "reserve"


class ClassroomAction(StrEnum):
    CREATE = BaseAction.CREATE
    READ = BaseAction.READ
    UPDATE = BaseAction.UPDATE
    DELETE = BaseAction.DELETE
    ALLOCATE = "allocate"
    RESERVE = "reserve"
    REQUEST = "request"


class CourseAction(StrEnum):
    CREATE = BaseAction.CREATE
    READ = BaseAction.READ
    UPDATE = BaseAction.UPDATE
    DELETE = BaseAction.DELETE


PermissionAction = ClassroomAction | CourseAction | BuildingAction

_ACTION_TRANSLATIONS: dict[str, str] = {
    BaseAction.CREATE: "criar",
    BaseAction.READ: "ler",
    BaseAction.UPDATE: "atualizar",
    BaseAction.DELETE: "excluir",
    "allocate": "alocar",
    "reserve": "reservar",
    "request": "solicitar",
}


def translate_action(action: PermissionAction) -> str:
    """Human-readable Portuguese verb for a permission action, meant to be
    embedded in "Usuário não tem permissão para <ação> ..." exception
    messages so it's evident which action was denied, not just that one was."""
    return _ACTION_TRANSLATIONS.get(str(action), str(action))
