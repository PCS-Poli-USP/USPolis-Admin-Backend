from sqlmodel import Session

from server.models.database.user_db_model import User
from server.services.security.access_scope import AccessScope
from server.services.security.role_permission_evaluator import build_permission_index


def access_scope_for(user: User, session: Session) -> AccessScope:
    """The AccessScope FastAPI would build for `user` (AccessScopeDep), for tests
    that construct adapters by hand. Build it after granting the user's roles:
    the permission index is a snapshot."""
    return AccessScope(
        user=user, session=session, permission_index=build_permission_index(user)
    )
