from datetime import datetime

from server.models.database.mobile_user_db_model import MobileUser
from server.models.dicts.base.forum_post_base_dict import ForumPostBaseDict
from server.models.dicts.database.base_database_dicts import BaseModelDict


class ForumPostModelDict(ForumPostBaseDict, BaseModelDict, total=False):
    """Forum post model dictionary for the database."""

    class_id: int | None
    subject_id: int
    reply_of_post_id: int | None
    user_id: int
    user: MobileUser
    created_at: datetime
    report_count: int
    replies_count: int
    enabled: bool
    likes_count: int
    filter_tags: int
