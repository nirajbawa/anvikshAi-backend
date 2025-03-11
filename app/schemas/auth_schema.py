from enum import Enum
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from app.models.user import EducationLevel, LanguagePreference
from fastapi import Form


class SignUpSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

class EmailBodySchema(BaseModel):
    otp: str
    
class VerifyOTPSchema(BaseModel):
    email: EmailStr = Field(...)
    otp: str = Field(...)
    
class SignInSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class User(BaseModel):
    email: str | None = None
    verified: bool | None = None

class Onboarding(BaseModel):
    first_name: str = Field(min_length=3)
    last_name: str = Field(min_length=3)
    dob: datetime
    bio: str = Field(min_length=300, max_length=1000)
    education: EducationLevel
    stream_of_education: str = Field(min_length=5)
    language_preference: LanguagePreference
    
class Token(BaseModel):
    access_token: str
    token_type: str
