from enum import StrEnum


class BaseAction(StrEnum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"


class ClassroomAction(StrEnum):
    CREATE = BaseAction.CREATE
    READ = BaseAction.READ
    UPDATE = BaseAction.UPDATE
    DELETE = BaseAction.DELETE
    ALLOCATE = "allocate"
    RESERVE = "reserve"


class CourseAction(StrEnum):
    CREATE = BaseAction.CREATE
    READ = BaseAction.READ
    UPDATE = BaseAction.UPDATE
    DELETE = BaseAction.DELETE


PermissionAction = ClassroomAction | CourseAction
