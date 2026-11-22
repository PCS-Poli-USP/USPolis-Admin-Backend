from typing import Annotated

from fastapi import Depends

from server.deps.authenticate import UserDep
from server.deps.permission_index_dep import PermissionIndexDep
from server.deps.session_dep import SessionDep
from server.services.security.access_scope import AccessScope


def access_scope(
    user: UserDep, session: SessionDep, permission_index: PermissionIndexDep
) -> AccessScope:
    return AccessScope(user=user, session=session, permission_index=permission_index)


# One per request (FastAPI caches dependencies), so its per-action cache is
# shared by every adapter in the request.
AccessScopeDep = Annotated[AccessScope, Depends(access_scope)]
