from fastapi import HTTPException, status
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


ALGORITHM = "HS256"


ACCESS_TOKEN_EXPIRE_MINUTES = 43200  # ✅ Fix: Use minutes, not days


class ExpertCoursesSerivce:
    @staticmethod
    async def get_courses(current_user: dict, page: int, limit: int) -> dict:
        try:
            total_courses = await TaskModel.find({"accepted": True, "rating": 0}, {"domains": {"$in": current_user.domains}}).count()
            courses = await TaskModel.find({"accepted": True, "rating": 0},
                                           {"domains": {"$in": current_user.domains}}
                                           ).skip((page - 1) * limit).limit(limit).to_list()

            # Convert to JSON
            data = [json.loads(task.model_dump_json()) for task in courses]

            # Pagination metadata
            response = {
                "total": total_courses,
                "page": page,
                "limit": limit,
                "total_pages": (total_courses // limit) + (1 if total_courses % limit != 0 else 0),
                "data": data
            }

            return response
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_course(cid: str) -> dict:
        try:
            course = await TaskModel.find_one({
                "_id": PydanticObjectId(cid),
                "accepted": True,
                "rating": 0
            })
            if not course:
                raise HTTPException(
                    status_code=400, detail="Invalid Task id.")
            data = json.loads(course.model_dump_json())
            return {"message": "Course fetched successfully!", "data": data}

        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def review_course(current_user: dict, cid: str, data: ExpertCourseReviewSchema) -> dict:
        try:
            course = await TaskModel.find_one({
                "_id": PydanticObjectId(cid),
                "accepted": True,
                "rating": 0
            })
            if not course:
                raise HTTPException(
                    status_code=400, detail="Invalid Task id.")

            await course.update({
                "$set": {
                    "feedback": data.feedback,
                    "rating": data.rating,
                    "reviewer": PydanticObjectId(current_user.id)
                }
            })

            user = await ExpertModel.find_one(
                {"_id": PydanticObjectId(current_user.id)},
            )

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            await user.update({
                "$set": {
                    "review_points": user.review_points+1,
                }
            })

            return {"message": "Feedback add successfully!"}

        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=str(e))
