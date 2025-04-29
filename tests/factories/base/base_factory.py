from abc import ABCMeta, abstractmethod
from typing import TypeVar

from faker import Faker

from server.models.dicts.base.base_dict import BaseDict

Dict = TypeVar("Dict", bound=BaseDict)


class BaseFactory(metaclass=ABCMeta):
    def __init__(self) -> None:
        self.faker = Faker("pt_BR")
        self.UPPER_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.LOWER_LETTERS = "abcdefghijklmnopqrstuvwxyz"
        self.DIGITS = "0123456789"

    @abstractmethod
    def get_base_defaults(self) -> BaseDict:
        """Return base default values common to models and requests"""
        pass
