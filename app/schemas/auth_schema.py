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


class Admin(BaseModel):
    email: str | None = None
    role: str | None = None
    verified: bool | None = None


class Expert(BaseModel):
    email: str | None = None
    role: str | None = None
    verified: bool | None = None


class Onboarding(BaseModel):
    first_name: str = Field(min_length=3)
    last_name: str = Field(min_length=3)
    dob: datetime
    bio: str = Field(min_length=50, max_length=90000)
    education: EducationLevel
    stream_of_education: str = Field(min_length=5)
    language_preference: LanguagePreference


class Token(BaseModel):
    access_token: str
    token_type: str


class ExpertInviteSchema(BaseModel):
    email: EmailStr = Field(...)


class ExpertOnboardingSchema(BaseModel):
    password: str = Field(min_length=6)
    first_name: str = Field(min_length=3)
    last_name: str = Field(min_length=3)
    bio: str = Field(min_length=50, max_length=90000)
    education: EducationLevel
    stream_of_education: str = Field(min_length=5)
    resume: str = Field(min_length=5)
    token: str = Field(...)


class ExpertEmailSchema(BaseModel):
    token: str
