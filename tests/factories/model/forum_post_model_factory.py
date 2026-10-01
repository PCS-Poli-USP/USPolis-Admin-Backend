from datetime import datetime
from typing import Unpack

from sqlmodel import Session

from server.models.database.class_db_model import Class
from server.models.database.forum_db_model import ForumPost
from server.models.database.mobile_user_db_model import MobileUser
from server.models.database.subject_db_model import Subject
from server.models.dicts.database.forum_post_database_dicts import ForumPostModelDict
from server.utils.must_be_int import must_be_int
from tests.factories.base.forum_post_base_factory import ForumPostBaseFactory
from tests.factories.model.base_model_factory import BaseModelFactory


class ForumPostModelFactory(BaseModelFactory[ForumPost]):
    def __init__(
        self,
        subject: Subject,
        user: MobileUser,
        session: Session,
        class_: Class | None = None,
        reply_of_post_id: int | None = None,
    ) -> None:
        super().__init__(session)
        self.subject = subject
        self.user = user
        self.class_ = class_
        self.reply_of_post_id = reply_of_post_id
        self.core_factory = ForumPostBaseFactory()

    def _get_model_type(self) -> type[ForumPost]:
        return ForumPost

    def get_defaults(self) -> ForumPostModelDict:
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "class_id": self.class_.id if self.class_ else None,
            "subject_id": must_be_int(self.subject.id),
            "reply_of_post_id": self.reply_of_post_id,
            "user_id": must_be_int(self.user.id),
            "user": self.user,
            "created_at": datetime.now(),
            "report_count": 0,
            "replies_count": 0,
            "enabled": True,
            "likes_count": 0,
            "filter_tags": 1,
        }

    def create(self, **overrides: Unpack[ForumPostModelDict]) -> ForumPost:  # type: ignore
        return super().create(**overrides)

    def create_and_refresh(  # type: ignore
        self, **overrides: Unpack[ForumPostModelDict]
    ) -> ForumPost:
        return super().create_and_refresh(**overrides)

    def update(  # type: ignore
        self, forum_post_id: int, **overrides: Unpack[ForumPostModelDict]
    ) -> ForumPost:
        return super().update(model_id=forum_post_id, **overrides)
