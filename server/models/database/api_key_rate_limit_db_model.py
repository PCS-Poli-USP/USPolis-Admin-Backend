from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlmodel import Field, Relationship

from server.models.database.base_db_model import BaseModel
from server.services.rate_limiter import RateLimitRule

if TYPE_CHECKING:
    from server.models.database.api_key_db_model import ApiKey


class ApiKeyRateLimit(BaseModel, table=True):
    """One "max_requests per window_seconds" rule of an API key. A key may
    have several (all enforced together); with none, the configured
    defaults apply, so a key is never unlimited."""

    __table_args__ = (
        UniqueConstraint(
            "api_key_id", "window_seconds", name="unique_api_key_rate_limit_window"
        ),
        CheckConstraint(
            "max_requests > 0", name="api_key_rate_limit_check_max_requests_positive"
        ),
        CheckConstraint(
            "window_seconds > 0",
            name="api_key_rate_limit_check_window_seconds_positive",
        ),
    )

    api_key_id: int = Field(foreign_key="apikey.id", ondelete="CASCADE", index=True)
    max_requests: int
    window_seconds: int

    api_key: "ApiKey" = Relationship(back_populates="rate_limits")

    def to_rule(self) -> RateLimitRule:
        return RateLimitRule(self.max_requests, self.window_seconds)
