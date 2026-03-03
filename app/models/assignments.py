from pydantic import Field, BaseModel
from beanie import Document, Link, PydanticObjectId
from typing import Optional, List
from datetime import datetime, timezone


class AssignmentModel(Document):
    assinments_question: str = Field(..., description="List of assignments")
    day:  PydanticObjectId = None
    user: PydanticObjectId = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    assinments_completed: bool = Field(
        default=False, description="Completion status")
    marks: Optional[int] = Field(
        default=0, description="marks (should be positive)")

    class Settings:
        collection = "videos"
