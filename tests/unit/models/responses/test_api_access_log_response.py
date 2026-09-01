from server.models.http.responses.api_access_log_response import ApiAccessLogResponse
from tests.utils.academic_test_utils import make_user
from tests.utils.api_log_test_utils import make_api_access_log


class TestApiAccessLogResponse:
    def test_from_access_log_with_a_user(self) -> None:
        user = make_user()
        log = make_api_access_log(
            endpoint="/api/classrooms", method="POST", status_code=201, user=user
        )

        data = ApiAccessLogResponse.from_access_log(log)

        assert data.id == log.id
        assert data.endpoint == "/api/classrooms"
        assert data.method == "POST"
        assert data.status_code == 201
        assert data.user_id == user.id
        assert data.user_email == user.email

    def test_from_access_log_without_a_user(self) -> None:
        log = make_api_access_log(user=None)

        data = ApiAccessLogResponse.from_access_log(log)

        assert data.user_id is None
        assert data.user_email is None

    def test_from_access_log_list(self) -> None:
        log1 = make_api_access_log()
        log2 = make_api_access_log()

        data = ApiAccessLogResponse.from_access_log_list([log1, log2])

        assert [d.id for d in data] == [log1.id, log2.id]
