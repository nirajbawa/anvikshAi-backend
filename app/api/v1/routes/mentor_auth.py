from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.services.mentor_auth_service import MentorAuthSerivce
from app.schemas.auth_schema import ExpertOnboardingSchema, SignInSchema, Expert, Mentor
from typing import Annotated
from app.core.security import get_current_active_mentor

mentor_auth = APIRouter()


@mentor_auth.post("/onboarding")
async def onboarding(data: ExpertOnboardingSchema):
    try:
        result = await MentorAuthSerivce.onboarding(data)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@mentor_auth.post("/sign-in")
async def sign_in(data: SignInSchema):
    try:
        result = await MentorAuthSerivce.sign_in(data)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@mentor_auth.get("/get-current-mentor")
async def get_current_user(
    current_user: Annotated[Mentor, Depends(get_current_active_mentor)],
):
    try:
        return current_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
