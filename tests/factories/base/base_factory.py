from abc import ABCMeta, abstractmethod
from typing import TypeVar

from faker import Faker

from server.models.dicts.base.base_dict import BaseDict

Dict = TypeVar("Dict", bound=BaseDict)

# Shared by every factory instance so `.unique.xxx()` calls (e.g. building
# names) actually dedupe across factories. The previous code created a fresh
# Faker instance per factory call and re-seeded it from the current timestamp,
# so a single test creating two buildings via two separate factory calls could
# have both draw the same "unique" name — harmless while every test truncated
# the database, but a real UniqueViolation once test isolation switched to
# per-test rollback. conftest.py's `_reset_faker_uniqueness` autouse fixture
# clears this instance's dedup tracking between tests, so it stays correct
# within a test without exhausting small-cardinality providers over the run.
shared_faker = Faker("pt_BR")


class BaseFactory(metaclass=ABCMeta):
    def __init__(self) -> None:
        self.faker = shared_faker
        self.UPPER_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.LOWER_LETTERS = "abcdefghijklmnopqrstuvwxyz"
        self.DIGITS = "0123456789"

    @abstractmethod
    def get_base_defaults(self) -> BaseDict:
        """Return base default values common to models and requests"""
        pass
