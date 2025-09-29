from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ChatMessageSchema(BaseModel):
    content: str = Field(..., min_length=1, description="The content of the message")

class AnswerItem(BaseModel):
    questionId: str
    selectedOption: str

class AnswerSubmission(BaseModel):
    answers: List[AnswerItem]
