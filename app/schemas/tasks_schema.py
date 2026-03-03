from pydantic import BaseModel, Field
from typing import List
from app.models.tasks import TaskLanguage


class TaskCreate(BaseModel):
    task_name: str = Field(min_length=3, max_length=100,
                           description="Title of the task")
    description: str = Field(min_length=10, max_length=2000,
                             default=None, description="Detailed task description")
    expected_duration_months: int = Field(
        description="Expected time duration in months")
    daily_hours: float = Field(
        le=24, description="Hours to be spent daily")
    language: TaskLanguage


class TaskAccept(BaseModel):
    accept: bool = Field(...,
                         description="Indicates whether the user accepts the generated task")


class UpdateDay(BaseModel):
    status: bool = Field(...,
                         description="Indicates whether the day is completed")


class ModifyTask(BaseModel):
    text: str = Field(...,
                      description="Indicates the text")

class CreateRoadmap(BaseModel):
    questions: List = Field(...,
                          description="Indicates the question")