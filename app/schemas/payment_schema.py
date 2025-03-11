from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from beanie import PydanticObjectId
from typing import Optional, List


class InsertOrderSchema(BaseModel):
    razorpay_order_id: str = Field(
        default="", description="marks (should be positive)")
