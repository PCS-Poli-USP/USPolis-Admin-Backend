from abc import ABCMeta
from typing import Any


class BaseRequestFactory(metaclass=ABCMeta):
    def __init__(self) -> None:
        pass

    def override_default_dict(
        self, default: dict[str, Any], overrides: dict[str, Any] | None
    ) -> None:
        """Update a TypedDict with overrides."""
        if overrides:
            for key, value in overrides.items():
                default[key] = value
