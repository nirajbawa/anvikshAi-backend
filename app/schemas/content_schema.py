from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from beanie import PydanticObjectId
from typing import Optional, List


class ContentStatus(BaseModel):
    marks: int = Field(description="marks (should be positive)")
    status: bool = Field(
        default=False, description="Completion status")


class QuizStatus(BaseModel):
    questions: List = Field(
        default=[], description="List of questions")


class Feedback(BaseModel):
    questions: List = Field(
        default=[], description="List of chats")
