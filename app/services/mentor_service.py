from fastapi import HTTPException, status
from app.services.task_service import TaskService
from app.schemas.auth_schema import ExpertOnboardingSchema, SignInSchema
from app.models.tasks import TaskModel
from app.models.mentor import MentorModel
from app.models.user import UserModel
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
from bson import ObjectId


class MentorService:
    @staticmethod
    async def get_dashboard(current_user: dict) -> dict:
        try:
            total_courses = await TaskModel.find({"mentor": current_user.id}).count()
            return {"message": "Mentor stats fetch successfully...!", "data":{
                "total_courses": total_courses
            }}
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=str(e))
        
        
    async def get_courses(current_user: dict) -> dict:
        try:
            
            tasks_pipeline = [
                {
                    "$match": {  
                        "mentor": PydanticObjectId(current_user.id)  # Ensure the correct field name
                    }
                },
                {
                    "$lookup": {
                        "from": UserModel.get_collection_name(),
                        "localField": "user",
                        "foreignField": "_id",
                        "as": "user_details"
                    }
                },
                {
                    "$unwind": {
                        "path": "$user_details",
                        "preserveNullAndEmptyArrays": True  # Keep task even if user details not found
                    }
                },
                {
                    "$lookup": {
                        "from": MentorModel.get_collection_name(),
                        "localField": "mentor",
                        "foreignField": "_id",
                        "as": "mentor_details"
                    }
                },
                {
                    "$unwind": {
                        "path": "$mentor_details",
                        "preserveNullAndEmptyArrays": True  # Keep task even if mentor details not found
                    }
                }
            ]
            
            def convert_to_serializable(doc):
                if isinstance(doc, dict):
                    return {k: str(v) if isinstance(v, (ObjectId, PydanticObjectId))
                            else v.isoformat() if isinstance(v, datetime)
                            else convert_to_serializable(v) for k, v in doc.items()}
                elif isinstance(doc, list):
                    return [convert_to_serializable(i) for i in doc]
                return doc

            courses = await TaskModel.aggregate(tasks_pipeline).to_list()
            if (not courses):
                raise HTTPException(
                    status_code=404,
                    detail=f"No courses exists"
                )

            data = convert_to_serializable(courses)
            # data = [json.loads(task.model_dump_json())
            #         for task in courses]
            return {"message": "Courses fetch successfully...!", "data":data}
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_messages(current_user: dict, courseId: str) -> dict:
        try:
            course = await TaskModel.find_one({"_id": PydanticObjectId(courseId), "mentor": PydanticObjectId(current_user.id)})
            if (not course):
                raise HTTPException(
                    status_code=404,
                    detail=f"No course exists"
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
