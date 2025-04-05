from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from beanie import Document
from fastapi import HTTPException, BackgroundTasks, Query
from app.schemas.auth_schema import SignInSchema
from app.core.otp_generator import generate_otp
from app.core.security import verify_password, create_jwt_token
from app.models.admin import AdminModel
from datetime import datetime, timedelta, timezone
from app.services.auth_service import AuthService
from app.models.tasks import TaskModel
from app.schemas.auth_schema import ExpertInviteSchema, ExpertEmailSchema
import os
from app.models.mentor import MentorModel
from fastapi.templating import Jinja2Templates
from fastapi_mail import FastMail, MessageSchema
from app.core.email import conf
from beanie import PydanticObjectId
import json
import math
from bson import ObjectId

templates = Jinja2Templates(directory="app/email_templates")
ACCESS_TOKEN_EXPIRE_MINUTES = 7200  # ✅ Fix: Use minutes, not days



class MentorProjection(BaseModel):
    id: Optional[PydanticObjectId] = Field(alias="_id")
    email: Optional[EmailStr]
    first_name: Optional[str]
    last_name: Optional[str]
    bio: Optional[str]
    education: Optional[str]
    stream_of_education: Optional[str]
    resume: Optional[str]
    created_at: Optional[datetime]
    verified: Optional[bool]
    onboarding: Optional[bool]
    domains: Optional[List[str]]


class AdminMentorService:
    @staticmethod
    async def invite_mentor(data: ExpertInviteSchema, background_tasks: BackgroundTasks) -> str:
        try:
            expert = await MentorModel.find_one({"email": data.email})
            if expert:
                if expert.onboarding == True:
                    raise HTTPException(
                        status_code=400, detail="Email already exists!")
                elif expert.onboarding == False:
                    pass
            else:
                expert_data = MentorModel(
                    email=data.email,
                    verified=True,
                    onboarding=False
                )
                await expert_data.insert()

            token = create_jwt_token({"email": data.email}, os.getenv(
                "MENTOR_SECRET_KEY"), timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
            print(token)
            email_body = ExpertEmailSchema(token=token)
            background_tasks.add_task(
                AdminMentorService.send_email, data.email, "Email Invitation For Mentor", email_body)

            return {"message": "Invitation sent successfully!", "success": True}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def send_email(recipient: str, subject: str, body: ExpertEmailSchema) -> None:
        template_data = {
            "invitation_url": f"{os.getenv('FRONT_END_URL')}/mentor-onboarding/{body.token}"}
        html_content = templates.get_template(
            "expert_email.html").render(template_data)

        message = MessageSchema(
            recipients=[
                recipient], subject=subject, body=html_content, subtype="html"
        )

        mail = FastMail(conf)
        await mail.send_message(message)
        
        
    @staticmethod
    async def get_mentors(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)) -> dict:
        try:
            # Count total users
            total_users = await MentorModel.find().count()

            if total_users == 0:
                raise HTTPException(status_code=404, detail="No users found")

            # Calculate pagination values
            skip = (page - 1) * limit
            total_pages = math.ceil(total_users / limit)
            
            pipeline = [
                {
                    "$lookup": {
                        "from": TaskModel.get_collection_name(),  # collection name in lowercase
                        "localField": "_id",
                        "foreignField": "mentor",
                        "as": "tasks"
                    }
                },
                {
                    "$addFields": {
                        "mentoring_count": { "$size": "$tasks" }
                    }
                },
                {
                    "$project": {
                        "password": 0,   
                    }
                },
                {
                    "$skip": skip
                },
                {
                    "$limit": limit
                }
            ]


            # Fetch mentor with pagination
            data = await MentorModel.aggregate(pipeline).to_list()
            def convert_to_serializable(doc):
                        if isinstance(doc, dict):
                            return {k: str(v) if isinstance(v, (ObjectId, PydanticObjectId))
                                    else v.isoformat() if isinstance(v, datetime)
                                    else convert_to_serializable(v) for k, v in doc.items()}
                        elif isinstance(doc, list):
                            return [convert_to_serializable(i) for i in doc]
                        return doc

            sanitize_data = convert_to_serializable(data)

            return {
                "message": "Data fetched successfully",
                "total_users": total_users,
                "total_pages": total_pages,
                "current_page": page,
                "users": sanitize_data
            }

        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=str(e))

