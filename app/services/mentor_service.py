from fastapi import HTTPException, status
from app.services.task_service import TaskService
from app.schemas.auth_schema import ExpertOnboardingSchema, SignInSchema
from app.models.tasks import TaskModel
from app.models.mentor import MentorModel
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


class MentorService:
    @staticmethod
    async def request_mentor(current_user: dict, courseId: str) -> dict:
        try:
            course = await TaskModel.find_one({"_id": PydanticObjectId(courseId), "mentor": None, "user": PydanticObjectId(current_user.id)})
            if not course:
                raise HTTPException(
                    status_code=400, detail="Invalid Task id.")
            elif course.completed == True:
                raise HTTPException(
                    status_code=400, detail="Course is already completed it is not possible to allocate mentor for this.")
            print(course)
            mentor = await MentorModel.find_one({"domains": {"$in": course.domains}})
            print(mentor)
            courses = await TaskModel.find({"mentor": PydanticObjectId(mentor.id), "completed": False}).count()
            if (courses <= 100):
                await course.update({
                    "$set": {
                        "mentor": PydanticObjectId(mentor.id)
                    }
                })
            return {"message": "Mentor allocated successfully.!", "data": {
                "mentor": str(mentor.id)
            }}
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=str(e))
