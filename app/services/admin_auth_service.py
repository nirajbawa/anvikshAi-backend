from fastapi import HTTPException, BackgroundTasks
from app.schemas.auth_schema import SignInSchema
from app.core.otp_generator import generate_otp
from app.core.security import verify_password, create_jwt_token
from app.models.admin import AdminModel
from datetime import datetime, timedelta, timezone
from app.services.auth_service import AuthService
from app.schemas.auth_schema import EmailBodySchema, Token
import os


ACCESS_TOKEN_EXPIRE_MINUTES = 43200  # ✅ Fix: Use minutes, not days


class AdminAuthService:
    @staticmethod
    async def sign_in(data: SignInSchema,  background_tasks: BackgroundTasks) -> str:
        try:
            admin = await AdminModel.find_one({"email": data.email})
            if not admin:
                raise HTTPException(status_code=400, detail="Invalid email.")

            if not verify_password(data.password, admin.password):
                raise HTTPException(
                    status_code=400, detail="Invalid email or password.")

            otp = generate_otp(6)
            expiry_time = datetime.now(
                timezone.utc) + timedelta(minutes=3)  # ✅ Ensure UTC timezone

            await admin.update(
                {"$set": {
                    "verify_code": otp,
                    "expiry_time": expiry_time
                }}
            )

            # Send OTP email
            email_body = EmailBodySchema(otp=otp)
            background_tasks.add_task(
                AuthService.send_email, data.email, "Email Verification", email_body)

            return {"message": "Please verify your email. Check your inbox for the verification code.", "success": True}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def verify_otp(email: str, otp: str):
        try:
            admin = await AdminModel.find_one({"email": email, "verify_code": otp})
            if not admin:
                raise HTTPException(
                    status_code=400, detail="Invalid OTP or admin not found.")

            # ✅ Ensure both datetime values have timezone info
            if admin.expiry_time.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=400, detail="OTP expired. Please request a new OTP.")

            token = create_jwt_token({"sub": admin.email, "role": "admin", "verified": True}, os.getenv(
                "ADMIN_SECRET_KEY"), timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
            # ✅ Fix: Convert to dict before returning
            return Token(access_token=token, token_type="bearer").dict()

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
