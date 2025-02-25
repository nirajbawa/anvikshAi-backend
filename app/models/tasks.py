from typing import Optional, List
from datetime import datetime, timezone
from pydantic import Field, BaseModel
from beanie import Document, Link
from enum import Enum
from models.user import UserModel

# Task Language Enum
class TaskLanguage(str, Enum):
    ENGLISH = "English"
    HINDI = "Hindi"

# Change DayTaskSchema to a Pydantic Model (BaseModel instead of Document)
class DayTaskSchema(BaseModel):
    day_no: int = Field(gt=0, description="Day number (should be positive)")
    task: str = Field(min_length=3, max_length=500)
    status: bool = Field(default=False, description="Completion status")

# Task Model
class TaskModel(Document):
    task_name: str = Field(min_length=3, max_length=100)
    description: str = Field(None, min_length=10, max_length=2000)
    expected_duration_months: int = Field(gt=0, description="Duration in months") 
    daily_hours: float = Field(gt=0, le=24, description="Hours spent daily")  
    language: TaskLanguage
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  
    day_wise_tasks: Optional[List[DayTaskSchema]] = Field(default=[], description="List of daily tasks")  
    roadmap_description: Optional[str] = None
    completed: Optional[bool] = Field(default=False)
    total_duration_in_days: Optional[int] = None
    user: Link[UserModel]  # Link to the UserModel
    generated_roadmap_text: Optional[str] = None
    
    class Settings:
        collection = "tasks"
