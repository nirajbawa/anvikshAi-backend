from fastapi import HTTPException, status
from app.services.task_service import TaskService
from app.schemas.auth_schema import ExpertOnboardingSchema, SignInSchema
from app.models.mentor import MentorModel
from jwt.exceptions import InvalidTokenError
import jwt
import os
import json
from app.core.chat_gpt import chat
from app.core.security import verify_password, create_jwt_token, hash_password
from datetime import timedelta
from app.schemas.auth_schema import Token

ALGORITHM = "HS256"


ACCESS_TOKEN_EXPIRE_MINUTES = 43200  # ✅ Fix: Use minutes, not days


class MentorAuthSerivce:
    @staticmethod
    async def onboarding(data: ExpertOnboardingSchema) -> dict:
        try:

            credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

            payload = jwt.decode(data.token, os.getenv(
                "MENTOR_SECRET_KEY"), algorithms=[ALGORITHM])

            email: str = payload.get("email")
            if email is None:
                raise credentials_exception

            expert = await MentorModel.find_one({
                "email": email,
                "onboarding": False
            })

            if not expert:
                raise HTTPException(
                    status_code=400, detail="User not found!")

            messages = (
                "You are an mentor categorization agent. Your task is to analyze the given resume and bio, education, stream of education to determine the mentor's primary domain(s) (ex: software engineering) of expertise. "
                "Based on the provided information, identify the most relevant field(s) in which the expert has significant skills and experience.\n\n"
                f"Bio: {data.bio}\n"
                f"Resume: {data.resume}\n\n"
                f"education: {data.education}"
                f"stream of education: {data.stream_of_education}"
                "Strictly return the output in the following JSON format:\n"
                '{"domains": ["Domain Name"]}\n'
                "If no valid domain is found or if an error occurs, return exactly:\n"
                '{"domains": []}\n'
                "Do not include any additional text, explanations, acknowledgments, or formatting outside of this JSON response."
            )

            chat_response = chat(messages)
            cleaned_output = TaskService.clean_json_output(chat_response)
            filtered_response = json.loads(cleaned_output)

            password = hash_password(data.password)

            domains = list(map(str.lower, filtered_response["domains"]))

            await expert.update({
                "$set": {
                    "first_name": data.first_name,
                    "last_name": data.last_name,
                    "password": password,
                    "bio": data.bio,
                    "education": data.education,
                    "stream_of_education": data.stream_of_education,
                    "resume": data.resume,
                    "onboarding": True,
                    "domains": domains
                }
            })

            token = create_jwt_token({"sub": email, "role": "mentor", "verified": expert.verified}, os.getenv(
                "MENTOR_SECRET_KEY"), timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

            return Token(access_token=token, token_type="bearer").dict()
        except InvalidTokenError:
            raise credentials_exception
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def sign_in(data: SignInSchema) -> dict:
        try:
            expert = await MentorModel.find_one({
                "email": data.email,
                "verified": True
            })

            if not expert:
                raise HTTPException(
                    status_code=400, detail="Invalid email or password.")
            if not verify_password(data.password, expert.password):
                raise HTTPException(
                    status_code=400, detail="Invalid email or password.")

            token = create_jwt_token({"sub": data.email, "role": "mentor"}, os.getenv(
                "MENTOR_SECRET_KEY"), timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

            return Token(access_token=token, token_type="bearer").dict()
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=str(e))
