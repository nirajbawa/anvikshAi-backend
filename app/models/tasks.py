from typing import Optional, List
from datetime import datetime, timezone
from pydantic import Field, BaseModel
from beanie import Document, Link, PydanticObjectId
from enum import Enum
from app.models.user import UserModel

# Task Language Enum


class TaskLanguage(str, Enum):
    ENGLISH = "English"
    HINDI = "Hindi"

# Change DayTaskSchema to a Pydantic Model (BaseModel instead of Document)


class DayTaskSchema(BaseModel):
    day: int = Field(gt=0, description="Day number (should be positive)")
    topics: str = Field(min_length=3)
    status: bool = Field(default=False, description="Completion status")

# Task Model


class TaskModel(Document):
    task_name: str = Field(min_length=3, max_length=100)
    description: str = Field(None, min_length=10, max_length=2000)
    expected_duration_months: int = Field(description="Duration in months")
    daily_hours: float = Field(description="Hours spent daily")
    language: TaskLanguage
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    roadmap_description: Optional[str] = None
    completed: Optional[bool] = Field(default=False)
    total_duration_in_days: Optional[int] = None
    user: Optional[PydanticObjectId] = None
    generated_roadmap_text: Optional[str] = None
    accepted: Optional[bool] = False
    questionnaire: Optional[List] = Field(default=[], description="List of questions")
    roadmap_phases: Optional[List] = Field(
        default=[], description="List of roadmap phases")

    class Settings:
        json_encoders = {PydanticObjectId: str}
        collection = "tasks"
