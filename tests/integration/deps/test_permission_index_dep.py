from server.deps.permission_index_dep import permission_index
from server.models.database.user_db_model import User
from server.services.security.role_permission_evaluator import PermissionIndex


class TestPermissionIndex:
    def test_builds_a_permission_index_for_the_user(self, admin_user: User) -> None:
        index = permission_index(user=admin_user)

        assert isinstance(index, PermissionIndex)
        assert index.is_admin is True
