from pydantic import Field, BaseModel
from beanie import Document, Link, PydanticObjectId
from typing import Optional, List
from datetime import datetime, timezone


class DayModel(Document):
    day: int = Field(gt=0, description="Day number (should be positive)")
    topics: str = Field(min_length=3, max_length=500)
    status: bool = Field(default=False, description="Completion status")
    belongs_to: PydanticObjectId = None
    leaning_topics: Optional[List] = Field(
        default=[], description="List of topics")
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    feedback:  Optional[str] = Field(None, min_length=10, max_length=2000)
    content: Optional[bool] = Field(
        default=False, description="Completion status")
    user: PydanticObjectId = None
    video: Optional[PydanticObjectId] = None
    quiz: Optional[PydanticObjectId] = None
    assignment: Optional[PydanticObjectId] = None
    article: Optional[PydanticObjectId] = None

    class Settings:
        collection = "days"
