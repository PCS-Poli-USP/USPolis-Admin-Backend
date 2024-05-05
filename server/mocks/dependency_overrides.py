from server.config import CONFIG
from server.mocks.dependencies.authenticate_mock import authenticate_mock
from server.services.auth.authenticate import authenticate

overrides = {}

if CONFIG.override_auth:
    overrides[authenticate] = authenticate_mock
