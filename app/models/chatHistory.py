from typing import List, Dict
from datetime import datetime, timezone
from beanie import Document
from pydantic import Field

class ChatMessage(Document):
    user_id: str
    window_id: str
    messages: List[Dict] = Field(default_factory=list)
    eq_iq_tests: List[Dict] = Field(default_factory=list)  # <-- NEW
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        collection = "chatHistory"