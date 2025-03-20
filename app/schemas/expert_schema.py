from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from beanie import PydanticObjectId
from typing import Optional, List


class ExpertCourseReviewSchema(BaseModel):
    feedback: str = Field(...)
    rating: float = Field(..., ge=1, le=5,
                          description="Rating must be between 1 and 5")
