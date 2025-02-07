from models.user import UserModel
from core.security import hash_password
from schemas.user_schema import UserSchema
from fastapi_mail import FastMail, MessageSchema
from core.email import conf
from fastapi.templating import Jinja2Templates
from schemas.user_schema import EmailBodySchema
from core.otp_generator import generate_otp
from fastapi import HTTPException
from datetime import datetime, timedelta

templates = Jinja2Templates(directory="app/email_templates")

class AuthService:
    @staticmethod
    async def check_user_exists(user_email: str) -> bool:
        user = await UserModel.find_one({"email": user_email})
        if user:
            return True
        return False
    
    @staticmethod
    async def create_user(data: UserSchema) -> str:
        try:
          
            password = hash_password(data.password)
            otp = generate_otp(6)

            user = UserModel(
                email=data.email, 
                password=password, 
                first_name=data.first_name, 
                last_name=data.last_name,
                dob=data.dob, 
                bio=data.bio, 
                education=data.education, 
                stream_of_education=data.stream_of_education,
                language_preference=data.language_preference,
                verified=False,
                expiry_time=datetime.utcnow() + timedelta(minutes=3),
                verify_code=otp  # Storing generated OTP
            )
            await user.insert()  # Corrected insertion

            # Send OTP email
            email_body = EmailBodySchema(user_name=data.first_name, otp=otp)
            await AuthService.send_email(data.email, "Email Verification", email_body)
            
            return "Please verify your email. Check your inbox for the verification code."

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def send_email(recipient: str, subject: str, body: EmailBodySchema) -> None:
        template_data = {
            "user_name": body.user_name,
            "otp_code": body.otp,
        }
            
        html_content = templates.get_template("otp_email.html").render(template_data)
        
        message = MessageSchema(
            recipients=[recipient],
            subject=subject,
            body=html_content,
            subtype="html"
        )

        mail = FastMail(conf)
        mail = await mail.send_message(message)
        print(mail)
