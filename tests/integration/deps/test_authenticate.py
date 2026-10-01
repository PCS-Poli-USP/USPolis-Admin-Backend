from unittest.mock import patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session

from server.config import CONFIG
from server.deps.authenticate import (
    AdminAccessRequired,
    InvalidToken,
    RestrictedAccessRequired,
    admin_authenticate,
    building_authenticate,
    google_token_authenticate,
    health_token_authenticate,
    restricted_authenticate,
)
from server.models.database.building_db_model import Building
from server.models.database.group_db_model import Group
from server.models.database.user_db_model import User
from server.repositories.building_repository import BuildingNotFound
from server.utils.must_be_int import must_be_int
from tests.factories.model.building_model_factory import BuildingModelFactory

_GET_USER_INFO_TARGET = "server.deps.authenticate.AuthenticationClient.get_user_info"


class TestHealthTokenAuthenticate:
    def test_accepts_the_configured_api_key(self) -> None:
        health_token_authenticate(x_api_key=CONFIG.health_api_key)

    def test_rejects_a_wrong_api_key(self) -> None:
        with pytest.raises(HTTPException) as exc_info:
            health_token_authenticate(x_api_key="wrong-key")

        assert exc_info.value.status_code == 401


class TestGoogleTokenAuthenticate:
    def test_raises_when_no_credentials_are_given(self) -> None:
        with pytest.raises(InvalidToken):
            google_token_authenticate(credentials=None)  # type: ignore[arg-type]

    def test_raises_when_credentials_have_no_token(self) -> None:
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="")

        with pytest.raises(InvalidToken):
            google_token_authenticate(credentials=credentials)

    def test_returns_authentication_client_result(self) -> None:
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="a-token")

        with patch(_GET_USER_INFO_TARGET, return_value="user-info") as mock_get_user_info:
            result = google_token_authenticate(credentials=credentials)

        mock_get_user_info.assert_called_once_with("a-token")
        assert result == mock_get_user_info.return_value


class TestRestrictedAuthenticate:
    def test_admin_bypasses_the_group_check(self, admin_user: User) -> None:
        assert restricted_authenticate(user=admin_user) is admin_user

    def test_allows_a_user_with_at_least_one_group(
        self, restricted_user: User, group: Group
    ) -> None:
        assert restricted_authenticate(user=restricted_user) is restricted_user

    def test_denies_a_user_with_no_groups(self, common_user: User) -> None:
        with pytest.raises(RestrictedAccessRequired):
            restricted_authenticate(user=common_user)


class TestAdminAuthenticate:
    def test_allows_an_admin(self, admin_user: User) -> None:
        admin_authenticate(user=admin_user)

    def test_denies_a_non_admin(self, restricted_user: User, group: Group) -> None:
        with pytest.raises(AdminAccessRequired):
            admin_authenticate(user=restricted_user)


class TestBuildingAuthenticate:
    def test_admin_can_access_any_building(
        self, admin_user: User, building: Building, session: Session
    ) -> None:
        found = building_authenticate(
            user=admin_user, session=session, building_id=must_be_int(building.id)
        )

        assert found.id == building.id

    def test_allows_a_user_who_owns_the_building(
        self, restricted_user: User, building: Building, session: Session
    ) -> None:
        found = building_authenticate(
            user=restricted_user, session=session, building_id=must_be_int(building.id)
        )

        assert found.id == building.id

    def test_denies_a_user_who_does_not_own_the_building(
        self, restricted_user: User, admin_user: User, session: Session
    ) -> None:
        other_building = BuildingModelFactory(admin_user, session).create_and_refresh()

        with pytest.raises(HTTPException) as exc_info:
            building_authenticate(
                user=restricted_user,
                session=session,
                building_id=must_be_int(other_building.id),
            )

        assert exc_info.value.status_code == 403

    def test_raises_for_an_unknown_building(
        self, common_user: User, session: Session
    ) -> None:
        with pytest.raises(BuildingNotFound):
            building_authenticate(user=common_user, session=session, building_id=-1)
