from abc import ABCMeta, abstractmethod
from typing import Any, Generic, TypeVar, Unpack
from sqlmodel import SQLModel, Session
from sqlalchemy.exc import NoResultFound

from server.models.dicts.database.base_database_dicts import BaseModelDict


M = TypeVar("M", bound=SQLModel)
InputType = TypeVar("InputType", bound=BaseModelDict)


class BaseModelFactory(Generic[M], metaclass=ABCMeta):
    """Base class to instantiate SQLModel models with default values.\n
    You should override the get_defaults method to provide default values for your model.\n
    The create method will merge the defaults with any overrides you provide.
    """

    CREATE_MANY_DEFAULT_COUNT = 5

    def __init__(self, session: Session) -> None:
        self.session = session

    @abstractmethod
    def _get_model_type(self) -> type[M]:
        pass

    @abstractmethod
    def get_defaults(self) -> BaseModelDict:
        pass

    def refresh(self, model: M) -> None:
        """Refresh the model instance from the database."""
        self.session.refresh(model)

    def refresh_many(self, models: list[M]) -> None:
        """Refresh the model instances from the database."""
        for model in models:
            self.session.refresh(model)

    def commit(self) -> None:
        """Commit the session"""
        self.session.commit()

    def __update_default_dict(
        self, default: dict[str, Any], overrides: dict[str, Any] | None
    ) -> None:
        """Update a TypedDict with overrides."""
        if overrides:
            for key, value in overrides.items():
                if key in default:
                    default[key] = value

    def _instanciate_model(self, overrides: dict[str, Any] | None = None) -> M:
        defaults = self.get_defaults()
        if overrides:
            self.__update_default_dict(defaults, overrides)  # type: ignore
        model = self._get_model_type()(**defaults)
        return model

    def create(self, **overrides: Unpack[InputType]) -> M:  # type: ignore
        """Create a model instance without commit the session"""
        model = self._instanciate_model(overrides)
        self.session.add(model)
        return model

    def create_and_refresh(self, **overrides: Unpack[InputType]) -> M:  # type: ignore
        """Create a model instance, commit the session and return the instance refreshed."""
        model = self.create(**overrides)
        self.commit()
        self.refresh(model)
        return model

    def create_many_default(self, count: int = CREATE_MANY_DEFAULT_COUNT) -> list[M]:
        """Create a list of model instances with default values. Count is 5 for default."""
        models: list[M] = []
        for _ in range(count):
            model = self._instanciate_model()
            models.append(model)
            self.session.add(model)
        return models

    def get_by_id(self, id: int) -> M:
        """Get a model instance by its ID.\n
        If the instance is not found, it raises a NoResultFound exception.
        """
        instance = self.session.get(self._get_model_type(), id)
        if instance is None:
            raise NoResultFound(f"Model with id {id} not found")
        return instance

    def update(self, model_id: int, **overrides: Unpack[InputType]) -> M:  # type: ignore
        """Update a model instance by its ID.\n
        The values will be the defaults, unless overridden.\n
        """
        defaults = self.get_defaults()
        if overrides:
            self.__update_default_dict(defaults, overrides)  # type: ignore
        model = self.get_by_id(model_id)
        for key, value in defaults.items():
            if value is not None:
                setattr(model, key, value)
        self.session.refresh(model)
        return model
