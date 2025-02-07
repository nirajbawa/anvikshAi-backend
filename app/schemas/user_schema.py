from enum import Enum
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class EducationLevel(str, Enum):
    BACHELORS = "Bachelors"
    MASTERS = "Masters"
    PHD = "PhD"


class LanguagePreference(str, Enum):
    ENGLISH = "English"
    HINDI = "Hindi"

class UserSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)
    first_name: str = Field(..., min_length=3)
    last_name: str = Field(..., min_length=3)
    dob: datetime
    bio: str = Field(..., min_length=300, max_length=1000)
    education: EducationLevel
    stream_of_education: str = Field(..., min_length=20)
    language_preference: LanguagePreference

class EmailBodySchema(BaseModel):
    otp: str
    user_name: str