from pydantic import Field
from beanie import Document, PydanticObjectId
from typing import Optional, List
from datetime import datetime, timezone


class CertificateModel(Document):
    task_id: PydanticObjectId = None
    user: PydanticObjectId = None
    task_name: str = Field(description="name of task")
    link: str = Field(description="name of task")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        collection = "certificates"