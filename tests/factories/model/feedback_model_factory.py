from typing import Unpack
from sqlmodel import Session
from server.models.database.feedback_db_model import Feedback
from server.models.database.user_db_model import User
from server.models.dicts.database.feedback_database_dicts import FeedbackModelDict
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.must_be_int import must_be_int
from tests.factories.base.feedback_base_factory import FeedbackBaseFactory
from tests.factories.model.base_model_factory import BaseModelFactory


class FeedbackFactory(BaseModelFactory[Feedback]):
    def __init__(self, creator: User, session: Session):
        super().__init__(session)
        self.user = creator
        self.core_factory = FeedbackBaseFactory()

    def _get_model_type(self) -> type[Feedback]:
        return Feedback

    def get_defaults(self) -> FeedbackModelDict:
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "user_id": must_be_int(self.user.id),
            "user": self.user,
            "created_at": BrazilDatetime.now_utc(),
        }

    def create(self, **overrides: Unpack[FeedbackModelDict]) -> Feedback:  # type: ignore
        """Create a feedback instance with default values.\n
        A default feedback has a single schedule.\n
        """
        return super().create(**overrides)

    def create_and_refresh(self, **overrides: Unpack[FeedbackModelDict]) -> Feedback:  # type: ignore
        """Create a feedback instance with default values, commit and refresh it."""
        feedback = self.create(**overrides)
        self.session.commit()
        self.session.refresh(feedback)
        return feedback

    def update(self, class_id: int, **overrides: Unpack[FeedbackModelDict]) -> Feedback:  # type: ignore
        """Create a class instance with default values."""
        return super().update(model_id=class_id, **overrides)
