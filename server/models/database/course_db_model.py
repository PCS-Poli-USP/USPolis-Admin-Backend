from sqlmodel import Field
from datetime import datetime
from server.models.database.base_db_model import BaseModel
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.course_period_type_enum import CoursePeriodType

class Course(BaseModel, table=True):
    name: str = Field(unique=True)
    minimal_duration: int = Field()
    ideal_duration: int = Field()
    maximal_duration: int = Field()
    updated_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    updated_by_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=BrazilDatetime.now_utc)
    created_by_id: int = Field(foreign_key="user.id")
    period: "CoursePeriodType" = Field()
