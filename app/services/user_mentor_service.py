from fastapi import HTTPException, status
from app.services.task_service import TaskService
from app.schemas.auth_schema import ExpertOnboardingSchema, SignInSchema
from app.models.tasks import TaskModel
from app.models.mentor import MentorModel
from app.models.messages import MessageModel
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
from typing import Optional, List
from pydantic import EmailStr, Field
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel

class MentorProjection(BaseModel):
    id: Optional[PydanticObjectId] = Field(alias="_id")
    email: Optional[EmailStr]
    first_name: Optional[str]
    last_name: Optional[str]


class UserMentorService:
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

    @staticmethod
    async def get_mentor(current_user: dict, mentorId: str) -> dict:
        try:
            mentor = await MentorModel.find_one({"_id": PydanticObjectId(mentorId)}).project(MentorProjection)
            if (not mentor):
                raise HTTPException(
                    status_code=404,
                    detail=f"No mentor exists"
                )
            data = json.loads(mentor.model_dump_json())
            return {"message": "Mentor data fetched successfully.!", "data": data}
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_messages(current_user: dict, courseId: str) -> dict:
        try:
            course = await TaskModel.find_one({"_id": PydanticObjectId(courseId), "user": PydanticObjectId(current_user.id)})
            if (not course):
                raise HTTPException(
                    status_code=404,
                detail=f"No messages exists"
                )
            messages = await MessageModel.find({"course_id":courseId}).to_list()
            if (not messages):
                raise HTTPException(
                    status_code=404,
                    detail=f"Invalid message id"
                )
            data = [json.loads(task.model_dump_json())
                    for task in messages]
            return {"message": "message data fetched successfully.!", "data":data}
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=str(e))
