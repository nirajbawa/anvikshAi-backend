from pydantic import BaseModel, Field
from typing import Optional


class ChatMessageSchema(BaseModel):
    content: str = Field(..., min_length=1, description="The content of the message")
