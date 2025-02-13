from models.user import UserModel
from core.security import hash_password, verify_password, create_jwt_token
from fastapi_mail import FastMail, MessageSchema
from core.email import conf
from fastapi.templating import Jinja2Templates
from schemas.auth_schema import EmailBodySchema, SignUpSchema, Onboarding, Token
from core.otp_generator import generate_otp
from fastapi import HTTPException, BackgroundTasks
from datetime import datetime, timedelta, timezone
import os

templates = Jinja2Templates(directory="app/email_templates")

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # ✅ Fix: Use minutes, not days


class AuthService:
    @staticmethod
    async def check_user_exists(user_email: str) -> bool:
        return await UserModel.find_one({"email": user_email, "verified": True}) is not None

    @staticmethod
    async def create_user(data: SignUpSchema, background_tasks: BackgroundTasks) -> str:
        try:
            password = hash_password(data.password)
            otp = generate_otp(6)
            expiry_time = datetime.now(timezone.utc) + timedelta(minutes=3)  # ✅ Ensure UTC timezone

            existing_user = await UserModel.find_one({"email": data.email, "verified": False})
            if existing_user:
                await existing_user.update(
                    {"$set": {"password": password, "verify_code": otp, "expiry_time": expiry_time}}
                )
            else:
                user = UserModel(
                    email=data.email, password=password, verified=False,
                    expiry_time=expiry_time, verify_code=otp
                )
                await user.insert()

            # Send OTP email
            email_body = EmailBodySchema(otp=otp)
            background_tasks.add_task(AuthService.send_email, data.email, "Email Verification", email_body)

            return "Please verify your email. Check your inbox for the verification code."

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def send_email(recipient: str, subject: str, body: EmailBodySchema) -> None:
        template_data = {"otp_code": body.otp}
        html_content = templates.get_template("otp_email.html").render(template_data)

        message = MessageSchema(
            recipients=[recipient], subject=subject, body=html_content, subtype="html"
        )

        mail = FastMail(conf)
        await mail.send_message(message)

    @staticmethod
    async def verify_otp(email: str, otp: str):
        try:
            user = await UserModel.find_one({"email": email, "verify_code": otp, "verified": False})
            if not user:
                raise HTTPException(status_code=400, detail="Invalid OTP or user not found.")

            # ✅ Ensure both datetime values have timezone info
            if user.expiry_time.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
                raise HTTPException(status_code=400, detail="OTP expired. Please request a new OTP.")

            user.verified = True
            await user.save()

            return "Email verified successfully!"
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def sign_in(data) -> dict:
        user = await UserModel.find_one({"email": data.username, "verified": True})
        if not user:
            raise HTTPException(status_code=400, detail="Invalid email.")
        if not verify_password(data.password, user.password):
            raise HTTPException(status_code=400, detail="Invalid email or password.")

        token = create_jwt_token({"sub": user.email}, os.getenv("SECRET_KEY"), timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return Token(access_token=token, token_type="bearer").dict()  # ✅ Fix: Convert to dict before returning

    @staticmethod
    async def onboarding(email, data: Onboarding) -> str:
        result = await UserModel.find_one({"email": email}).update(
            {"$set": {
                "first_name": data.first_name, "last_name": data.last_name, "dob": data.dob,
                "bio": data.bio, "education": data.education, "stream_of_education": data.stream_of_education,
                "language_preference": data.language_preference, "onboarding": True
            }}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="User not found.")
        return "Onboarding completed successfully!"
