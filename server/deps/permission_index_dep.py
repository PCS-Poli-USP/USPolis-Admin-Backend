from typing import Annotated

from fastapi import Depends

from server.deps.authenticate import UserDep
from server.services.security.role_permission_evaluator import (
    PermissionIndex,
    build_permission_index,
)


def permission_index(user: UserDep) -> PermissionIndex:
    return build_permission_index(user)


PermissionIndexDep = Annotated[PermissionIndex, Depends(permission_index)]
