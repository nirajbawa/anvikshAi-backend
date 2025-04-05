from fastapi import HTTPException, status, Query
from app.services.task_service import TaskService
from app.schemas.auth_schema import ExpertOnboardingSchema, SignInSchema
from app.models.tasks import TaskModel
from app.models.expert import ExpertModel
from jwt.exceptions import InvalidTokenError
import jwt
import os
import json
from app.core.chat_gpt import chat
from app.core.security import verify_password, create_jwt_token, hash_password
from datetime import timedelta
from app.schemas.auth_schema import Token
from app.schemas.expert_schema import ExpertCourseReviewSchema
from beanie import PydanticObjectId
import math
from bson import ObjectId
from datetime import datetime


ALGORITHM = "HS256"


ACCESS_TOKEN_EXPIRE_MINUTES = 43200  # ✅ Fix: Use minutes, not days


class AdminCoursesSerivce:
    @staticmethod
    async def get_courses(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)) -> dict:
        try:

            total_courses = await TaskModel.find().count()

            if total_courses == 0:
                raise HTTPException(status_code=404, detail="No users found")

            skip = (page - 1) * limit
            total_pages = math.ceil(total_courses / limit)

            # courses = await TaskModel.find().skip(skip).limit(limit).to_list()

            courses_pipeline = [
                {
                    "$match": {
                        # Exclude reviewers with rating 0
                        "rating": {"$ne": 0}
                    }
                },
                {"$skip": skip},
                {"$limit": limit},
                {
                    "$lookup": {
                        # Dynamically get the collection name
                        "from": ExpertModel.get_collection_name(),
                        "localField": "reviewer",
                        "foreignField": "_id",
                        "as": "reviewer_details"
                    }
                },
                {
                    "$unwind": {
                        "path": "$reviewer_details",
                        "preserveNullAndEmptyArrays": False  # Keep courses even if no reviewer found
                    }
                }
            ]

            courses = await TaskModel.aggregate(courses_pipeline).to_list()

            def convert_to_serializable(doc):
                if isinstance(doc, dict):
                    return {k: str(v) if isinstance(v, (ObjectId, PydanticObjectId))
                            else v.isoformat() if isinstance(v, datetime)
                            else convert_to_serializable(v) for k, v in doc.items()}
                elif isinstance(doc, list):
                    return [convert_to_serializable(i) for i in doc]
                return doc

            courses = convert_to_serializable(courses)

            return {
                "message": "Data fetched successfully",
                "total_courses": total_courses,
                "total_pages": total_pages,
                "current_page": page,
                "courses": courses
            }

        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=str(e))
