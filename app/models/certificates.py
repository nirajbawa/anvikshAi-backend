from pydantic import Field
from beanie import Document, PydanticObjectId
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId


class CertificateModel(Document):
    task_id: PydanticObjectId = Field(
        default_factory=lambda: PydanticObjectId(ObjectId()), unique=True)
    user: Optional[PydanticObjectId] = None
    task_name: str = Field(description="name of task")
    # link: str = Field(description="certificate link")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        collection = "certificates"
