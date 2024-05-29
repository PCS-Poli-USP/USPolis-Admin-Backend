from typing import Any

from server.config import CONFIG
from server.deps.authenticate import authenticate
from server.deps.cognito_client import CognitoClient
from server.mocks.deps.authenticate_mock import authenticate_mock
from server.mocks.services.cognito_client_mock import CognitoClientMock

deps_overrides: dict[Any, Any] = {}

if CONFIG.override_auth:
    deps_overrides[authenticate] = authenticate_mock

if CONFIG.override_cognito_client:
    deps_overrides[CognitoClient] = CognitoClientMock

DepsOverrides = deps_overrides
