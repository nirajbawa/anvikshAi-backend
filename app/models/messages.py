from typing import Optional, List
from datetime import datetime, timezone
from pydantic import EmailStr, Field
from beanie import Document, Indexed
from enum import Enum


class MessageModel(Document):
    sender_id: str
    receiver_id: str
    course_id: str
    sender: str
    message: str
    timestamp: datetime

    class Settings:
        collection = "messages"