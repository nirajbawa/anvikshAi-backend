from pydantic import Field, BaseModel
from beanie import Document, Link, PydanticObjectId
from typing import Optional, List
from datetime import datetime, timezone


class ArticleModel(Document):
    articles_list: List = Field(
        default=[], description="List of videos")
    day:  PydanticObjectId = None
    user: PydanticObjectId = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    all_article_readed: bool = Field(
        default=False, description="Completion status")
    marks: Optional[int] = Field(
        default=0, description="marks (should be positive)")

    class Settings:
        collection = "articles"
