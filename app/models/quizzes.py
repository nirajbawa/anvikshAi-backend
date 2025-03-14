from pydantic import Field
from beanie import Document, PydanticObjectId
from typing import Optional, List
from datetime import datetime, timezone


class QuizModel(Document):
    questions: List = Field(
        default=[], description="List of questions")
    day:  PydanticObjectId = None
    user: PydanticObjectId = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    quiz_completed: bool = Field(
        default=False, description="Completion status")
    marks: Optional[int] = Field(
        default=0, description="marks (should be positive)")

    class Settings:
        collection = "quizzes"
