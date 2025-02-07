from enum import Enum
from beanie import Document, Indexed
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

# 🎯 Enum for Education Choices
class EducationLevel(str, Enum):
    BACHELORS = "Bachelors"
    MASTERS = "Masters"
    PHD = "PhD"

# 🎯 Enum for Language Preferences
class LanguagePreference(str, Enum):
    ENGLISH = "English"
    HINDI = "Hindi"

class UserModel(Document):
    email: EmailStr = Indexed(unique=True)  # Ensure uniqueness in MongoDB
    password: str
    first_name: str = Field(..., min_length=3)
    last_name: str = Field(..., min_length=3)
    dob: datetime
    bio: str = Field(..., min_length=300, max_length=1000)
    education: EducationLevel 
    stream_of_education: str = Field(..., min_length=5)  # Adjusted min_length
    language_preference: LanguagePreference  
    verified: bool = False
    verify_code: str = Field(..., min_length=6, max_length=6)  # Security fix
    expiry_time: datetime =  Field(...)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "users"
        indexes = [
            "email",  # Unique email index
        ]
