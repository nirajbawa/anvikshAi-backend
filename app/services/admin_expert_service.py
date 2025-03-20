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
from app.schemas.auth_schema import ExpertInviteSchema, ExpertEmailSchema
import os
from app.models.expert import ExpertModel
from fastapi.templating import Jinja2Templates
from fastapi_mail import FastMail, MessageSchema
from app.core.email import conf
from beanie import PydanticObjectId
import json
import math

templates = Jinja2Templates(directory="app/email_templates")
ACCESS_TOKEN_EXPIRE_MINUTES = 7200  # ✅ Fix: Use minutes, not days


class ExpertProjection(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    domains: Optional[List[str]]
    review_points: Optional[float]
    bio: Optional[str]
    education: Optional[str]
    stream_of_education: Optional[str]
    resume: Optional[str]
    created_at: Optional[datetime]
    onboarding: Optional[bool]
    review_points: Optional[float]

    class Config:
        from_attributes = True  # Allows conversion from DB model to Pydantic


class AdminExpertService:
    @staticmethod
    async def invite_expert(data: ExpertInviteSchema, background_tasks: BackgroundTasks) -> str:
        try:
            expert = await ExpertModel.find_one({"email": data.email})
            if expert:
                if expert.onboarding == True:
                    raise HTTPException(
                        status_code=400, detail="Email already exists!")
                elif expert.onboarding == False:
                    pass
            else:
                expert_data = ExpertModel(
                    email=data.email,
                    verified=True,
                    onboarding=False
                )
                await expert_data.insert()

            token = create_jwt_token({"email": data.email}, os.getenv(
                "EXPERT_SECRET_KEY"), timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
            print(token)
            email_body = ExpertEmailSchema(token=token)
            background_tasks.add_task(
                AdminExpertService.send_email, data.email, "Email Invitation For Expert", email_body)

            return {"message": "Invitation sent successfully!", "success": True}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def send_email(recipient: str, subject: str, body: ExpertEmailSchema) -> None:
        template_data = {
            "invitation_url": f"{os.getenv("FRONT_END_URL")}/expert-onboarding/{body.token}"}
        html_content = templates.get_template(
            "expert_email.html").render(template_data)

        message = MessageSchema(
            recipients=[
                recipient], subject=subject, body=html_content, subtype="html"
        )

        mail = FastMail(conf)
        await mail.send_message(message)

    @staticmethod
    async def get_experts(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)) -> dict:
        try:
            # Count total users
            total_users = await ExpertModel.find().count()

            if total_users == 0:
                raise HTTPException(status_code=404, detail="No users found")

            # Calculate pagination values
            skip = (page - 1) * limit
            total_pages = math.ceil(total_users / limit)

            # Fetch users with pagination
            users = await ExpertModel.find().project(ExpertProjection).skip(skip).limit(limit).to_list()

            # Exclude password from response
            data = [
                {key: value for key, value in json.loads(
                    user.model_dump_json()).items() if key != "password"}
                for user in users
            ]

            return {
                "message": "Data fetched successfully",
                "total_users": total_users,
                "total_pages": total_pages,
                "current_page": page,
                "users": data
            }

        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=str(e))
