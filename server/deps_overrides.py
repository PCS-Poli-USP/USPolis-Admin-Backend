from typing import Any

from server.config import CONFIG
from server.deps.authenticate import authenticate
from server.mocks.deps.authenticate_mock import authenticate_mock

deps_overrides: dict[Any, Any] = {}

if CONFIG.override_auth:
    deps_overrides[authenticate] = authenticate_mock

DepsOverrides = deps_overrides
