from typing import Optional
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


class LanguagePreference(str, Enum):
    ENGLISH = "English"
    HINDI = "Hindi"
    MARATHI = "Marathi"


class PremiumPackage(str, Enum):
    BASIC = "Basic"
    PREMIUM = "Premium"


class UserModel(Document):
    email: EmailStr = Indexed(unique=True)  # Ensure uniqueness
    password: str
    first_name: Optional[str] = Field(min_length=3, default=None)
    last_name: Optional[str] = Field(min_length=3, default=None)
    dob: Optional[datetime] = None  # ✅ Now Optional
    bio: Optional[str] = Field(
        min_length=0, max_length=1000, default=None)  # ✅ Allows empty bio
    education: Optional[EducationLevel] = None  # ✅ Now Optional
    stream_of_education: Optional[str] = None  # ✅ Default Empty String
    language_preference: Optional[LanguagePreference] = None  # ✅ Now Optional
    verified: bool = Field(default=False)
    verify_code: str = Field(min_length=6, max_length=6)
    expiry_time: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(
        timezone.utc))  # ✅ Ensures correct default behavior
    onboarding: bool = Field(default=False)
    premium_package: Optional[PremiumPackage] = Field(
        default=PremiumPackage.BASIC)  # ✅ Fixed Enum Default
    validTill: Optional[datetime] = None

    class Settings:
        collection = "users"
