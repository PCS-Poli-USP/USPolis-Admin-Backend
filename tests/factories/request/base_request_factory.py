from abc import ABCMeta
from typing import Any
from faker import Faker


class BaseRequestFactory(metaclass=ABCMeta):
    def __init__(self) -> None:
        self.faker = Faker("pt_BR")
        self.LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.DIGITS = "0123456789"

    def random_email(self) -> str:
        return self.faker.email(domain="usp.br")

    def override_default_dict(
        self, default: dict[str, Any], overrides: dict[str, Any] | None
    ) -> None:
        """Update a TypedDict with overrides."""
        if overrides:
            for key, value in overrides.items():
                default[key] = value
