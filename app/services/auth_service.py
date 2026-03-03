from app.models.user import UserModel
from app.core.security import hash_password, verify_password, create_jwt_token
from app.core.http_email import http_email_service  # Import the new service
from fastapi.templating import Jinja2Templates
from app.schemas.auth_schema import EmailBodySchema, SignUpSchema, Onboarding, Token
from app.core.otp_generator import generate_otp
from fastapi import HTTPException, BackgroundTasks
from datetime import datetime, timedelta, timezone
import os
import logging

templates = Jinja2Templates(directory="app/email_templates")

ACCESS_TOKEN_EXPIRE_MINUTES = 43200  

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    async def check_user_exists(user_email: str) -> bool:
        return await UserModel.find_one({"email": user_email, "verified": True}) is not None

    @staticmethod
    async def create_user(data: SignUpSchema, background_tasks: BackgroundTasks) -> str:
        try:
            password = hash_password(data.password)
            otp = generate_otp(6)
            expiry_time = datetime.now(timezone.utc) + timedelta(minutes=3)

            existing_user = await UserModel.find_one({"email": data.email, "verified": False})
            if existing_user:
                await existing_user.update(
                    {"$set": {"password": password, "verify_code": otp,
                              "expiry_time": expiry_time}}
                )
            else:
                user = UserModel(
                    email=data.email, password=password, verified=False,
                    expiry_time=expiry_time, verify_code=otp
                )
                await user.insert()

            # Send OTP email using HTTP request
            email_body = EmailBodySchema(otp=otp)
            background_tasks.add_task(
                AuthService.send_email, data.email, "Email Verification", email_body)

            return "Please verify your email. Check your inbox for the verification code."

        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def send_email(recipient: str, subject: str, body: EmailBodySchema) -> None:
        """
        Send email using HTTP request to EC2 instance with API key
        """
        try:
            # Render HTML template
            template_data = {"otp_code": body.otp}
            html_content = templates.get_template(
                "otp_email.html").render(template_data)

            # Send via HTTP with API key
            response = await http_email_service.send_email(
                recipient=recipient,
                subject=subject,
                html_content=html_content
            )
            
            logger.info(f"Email sent successfully to {recipient}")
            logger.debug(f"Email service response: {response}")
            
        except HTTPException as e:
            # Log specific HTTP exceptions
            if e.status_code == 401:
                logger.error(f"API key error for email service: {e.detail}")
            else:
                logger.error(f"Email service error for {recipient}: {e.detail}")
        except Exception as e:
            # Log the error but don't raise - this runs in background
            logger.error(f"Failed to send email to {recipient}: {str(e)}")

    @staticmethod
    async def verify_otp(email: str, otp: str):
        try:
            user = await UserModel.find_one({"email": email, "verify_code": otp, "verified": False})
            if not user:
                raise HTTPException(
                    status_code=400, detail="Invalid OTP or user not found.")

            if user.expiry_time.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=400, detail="OTP expired. Please request a new OTP.")

            user.verified = True
            await user.save()

            token = create_jwt_token({"sub": user.email}, os.getenv(
                "SECRET_KEY"), timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

            return Token(access_token=token, token_type="bearer").dict()
        except Exception as e:
            logger.error(f"Error verifying OTP: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def sign_in(data) -> dict:
        user = await UserModel.find_one({"email": data.username, "verified": True})
        if not user:
            raise HTTPException(
                status_code=400, detail="Invalid email or password.")
        if not verify_password(data.password, user.password):
            raise HTTPException(
                status_code=400, detail="Invalid email or password.")

        token = create_jwt_token({"sub": user.email}, os.getenv(
            "SECRET_KEY"), timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return Token(access_token=token, token_type="bearer").dict()

    @staticmethod
    async def onboarding(email, data: Onboarding) -> str:
        plan_expiry_date = datetime.now(timezone.utc) + timedelta(days=30)
        result = await UserModel.find_one({"email": email}).update(
            {"$set": {
                "first_name": data.first_name, "last_name": data.last_name, "dob": data.dob,
                "bio": data.bio, "education": data.education, "stream_of_education": data.stream_of_education,
                "language_preference": data.language_preference, "onboarding": True, "validTill": plan_expiry_date
            }}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="User not found.")
        return "Onboarding completed successfully!"