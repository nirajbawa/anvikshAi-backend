from typing import Optional
from datetime import datetime, timezone
from pydantic import EmailStr, Field
from beanie import Document, Indexed


class AdminModel(Document):
    email: EmailStr = Indexed(unique=True)  # Ensure uniqueness
    password: str
    role: str = Field(default="admin")
    verify_code: Optional[str] = Field(
        default=None, min_length=6, max_length=6)
    expiry_time: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(
        timezone.utc))  # ✅ Ensures correct default behavior

    class Settings:
        collection = "admins"
