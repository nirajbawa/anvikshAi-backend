from typing import Optional, List
from datetime import datetime, timezone
from pydantic import EmailStr, Field
from beanie import Document, Indexed
from enum import Enum

# Define Enums


class EducationLevel(str, Enum):
    HIGH_SCHOOL = "High School"
    BACHELORS = "Bachelors"
    MASTERS = "Masters"
    PHD = "PHD"


class ExpertModel(Document):
    email: EmailStr = Indexed(unique=True)  # Ensure uniqueness
    password: Optional[str] = None
    first_name: Optional[str] = Field(min_length=3, default=None)
    last_name: Optional[str] = Field(min_length=3, default=None)
    bio: Optional[str] = Field(
        min_length=0, max_length=90000, default=None)  # ✅ Allows empty bio
    education: Optional[EducationLevel] = None  # ✅ Now Optional
    stream_of_education: Optional[str] = None  # ✅ Default Empty String
    created_at: datetime = Field(default_factory=lambda: datetime.now(
        timezone.utc))  # ✅ Ensures correct default behavior
    verified: bool = Field(default=False)
    onboarding: Optional[bool] = Field(default=False)
    domains: Optional[List] = []
    resume: Optional[str] = Field(default=None)
    review_points: Optional[float] = Field(default=0)

    class Settings:
        collection = "experts"
