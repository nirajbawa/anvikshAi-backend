from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from models.tasks import TaskLanguage


class TaskCreate(BaseModel):
    task_name: str = Field(min_length=3, max_length=100, description="Title of the task")
    description: str = Field(min_length=10, max_length=2000, default=None, description="Detailed task description")
    expected_duration_months: int = Field(gt=0, description="Expected time duration in months")
    daily_hours: float = Field(gt=0, le=24, description="Hours to be spent daily")
    language: TaskLanguage