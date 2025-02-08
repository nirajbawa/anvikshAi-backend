from typing import Optional
from datetime import datetime
from pydantic import EmailStr, Field
from beanie import Document, Indexed
from enum import Enum

# Define Enums
class EducationLevel(str, Enum):
    HIGH_SCHOOL = "High School"
    BACHELORS = "Bachelors"
    MASTERS = "Masters"
    PHD = "PhD"

class LanguagePreference(str, Enum):
    ENGLISH = "English"
    HINDI = "Hindi"
    MARATHI = "Marathi"

class UserModel(Document):
    email: EmailStr = Indexed(unique=True)  # Ensure uniqueness
    password: str
    first_name: Optional[str] = Field(min_length=3, default=None)
    last_name: Optional[str] = Field(min_length=3, default=None)
    dob: Optional[datetime] = None  # ✅ Now Optional
    bio: Optional[str] = Field(min_length=300, max_length=1000, default=None)
    education: Optional[EducationLevel] = None  # ✅ Now Optional
    stream_of_education: Optional[str] = Field(min_length=5, default=None)  # ✅ Default Empty String
    language_preference: Optional[LanguagePreference] = None  # ✅ Now Optional
    verified: bool = Field(default=False)
    verify_code: str = Field(min_length=6, max_length=6)
    expiry_time: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    onboarding: bool = Field(default=False)

    class Settings:
        collection = "users"
