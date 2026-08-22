from collections.abc import Iterator
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from server.middlewares import LoggerMessage, LoggerMiddleware, get_client_ip


def make_request(
    headers: dict[str, str] | None = None, client_host: str | None = None
) -> Request:
    scope: dict[str, Any] = {
        "type": "http",
        "headers": [
            (key.lower().encode(), value.encode())
            for key, value in (headers or {}).items()
        ],
        "client": (client_host, 12345) if client_host else None,
        "method": "GET",
        "path": "/",
    }
    return Request(scope)


class TestGetClientIp:
    def test_uses_first_forwarded_for_entry(self) -> None:
        request = make_request(
            headers={"x-forwarded-for": "1.1.1.1, 2.2.2.2"}, client_host="9.9.9.9"
        )
        assert get_client_ip(request) == "1.1.1.1"

    def test_falls_back_to_client_host_without_header(self) -> None:
        request = make_request(client_host="9.9.9.9")
        assert get_client_ip(request) == "9.9.9.9"

    def test_returns_none_without_header_or_client(self) -> None:
        request = make_request()
        assert get_client_ip(request) is None


class TestLoggerMessageFormat:
    def test_includes_all_fields(self) -> None:
        message = LoggerMessage(
            method="POST",
            url=MagicMock(path="/subjects", query="foo=bar"),
            host="1.2.3.4",
            type="Response",
            user_email="user@usp.br",
            status_code=409,
            duration=0.001,
            response_detail="Integrity error",
            request_body='{"code":"MAC0110"}',
        )
        text = str(message)
        assert 'path="/subjects?foo=bar"' in text
        assert 'status="409"' in text
        assert 'response_detail="Integrity error"' in text
        assert 'request_body="{"code":"MAC0110"}"' in text

    def test_defaults_to_na_when_fields_missing(self) -> None:
        message = LoggerMessage(method="GET", url=MagicMock(path="/health", query=""))
        text = str(message)
        assert 'status="N/A"' in text
        assert 'response_detail="N/A"' in text
        assert 'request_body="N/A"' in text


def build_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(LoggerMiddleware)

    @app.post("/subjects")
    async def create_subject() -> JSONResponse:
        return JSONResponse(status_code=201, content={"message": "created"})

    @app.post("/subjects/duplicate")
    async def create_duplicate_subject() -> JSONResponse:
        return JSONResponse(status_code=409, content={"message": "Integrity error"})

    @app.post("/other")
    async def create_other() -> JSONResponse:
        return JSONResponse(status_code=409, content={"message": "Other conflict"})

    @app.get("/health")
    async def health() -> JSONResponse:
        return JSONResponse(status_code=200, content={"status": "ok"})

    return app


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(build_app()) as test_client:
        yield test_client


@pytest.fixture
def captured_logs(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    fake_info = MagicMock()
    monkeypatch.setattr("server.middlewares.logger.info", fake_info)
    return fake_info


@pytest.fixture
def captured_loki_logs(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    fake_info = MagicMock()
    monkeypatch.setattr("server.middlewares.loki_access_logger.info", fake_info)
    return fake_info


def response_lines(captured_logs: MagicMock) -> list[str]:
    return [
        call.args[0]
        for call in captured_logs.call_args_list
        if 'type="Response"' in call.args[0]
    ]


def request_lines(captured_logs: MagicMock) -> list[str]:
    return [
        call.args[0]
        for call in captured_logs.call_args_list
        if 'type="Request"' in call.args[0]
    ]


class TestRequestBodyOnErrorResponses:
    def test_matched_route_conflict_includes_request_body_on_response_line(
        self, client: TestClient, captured_logs: MagicMock
    ) -> None:
        payload = b'{"code":"MAC0110"}'
        client.post("/subjects/duplicate", content=payload)

        lines = response_lines(captured_logs)
        assert len(lines) == 1
        assert 'status="409"' in lines[0]
        assert 'response_detail="Integrity error"' in lines[0]
        assert 'request_body="{"code":"MAC0110"}"' in lines[0]

    def test_matched_route_success_does_not_include_body_on_response_line(
        self, client: TestClient, captured_logs: MagicMock
    ) -> None:
        payload = b'{"code":"MAC0110"}'
        client.post("/subjects", content=payload)

        assert 'request_body="N/A"' in response_lines(captured_logs)[0]
        # The body is still captured on the Request line regardless of status.
        assert 'request_body="{"code":"MAC0110"}"' in request_lines(captured_logs)[0]

    def test_unmatched_route_conflict_does_not_capture_body(
        self, client: TestClient, captured_logs: MagicMock
    ) -> None:
        payload = b'{"code":"MAC0110"}'
        client.post("/other", content=payload)

        lines = response_lines(captured_logs)
        assert 'request_body="N/A"' in lines[0]
        assert 'response_detail="Other conflict"' in lines[0]


class TestLokiAccessLog:
    def test_skips_excluded_paths(
        self, client: TestClient, captured_loki_logs: MagicMock
    ) -> None:
        client.get("/health")
        captured_loki_logs.assert_not_called()

    def test_emitted_for_regular_paths(
        self, client: TestClient, captured_loki_logs: MagicMock
    ) -> None:
        client.post("/subjects", content=b'{"code":"MAC0110"}')

        captured_loki_logs.assert_called_once()
        _, kwargs = captured_loki_logs.call_args
        extra = kwargs["extra"]
        assert extra["method"] == "POST"
        assert extra["path"] == "/subjects"
        assert extra["status_code"] == 201

    def test_skipped_for_options_requests(
        self, client: TestClient, captured_loki_logs: MagicMock
    ) -> None:
        client.options("/subjects")
        captured_loki_logs.assert_not_called()
