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
from app.models.mentor import MentorModel
from fastapi.templating import Jinja2Templates
from fastapi_mail import FastMail, MessageSchema
from app.core.email import conf
from beanie import PydanticObjectId
import json
import math

templates = Jinja2Templates(directory="app/email_templates")
ACCESS_TOKEN_EXPIRE_MINUTES = 7200  # ✅ Fix: Use minutes, not days


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
