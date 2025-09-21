from fastapi import APIRouter, HTTPException
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.schemas.auth_schema import SignUpSchema, VerifyOTPSchema, SignInSchema, User, Onboarding
from app.services.auth_service import AuthService
from fastapi import status, BackgroundTasks
from app.core.security import get_current_active_user
from fastapi.security import OAuth2PasswordRequestForm
from app.services.career_service import CareerService
from app.schemas.chat_message_schema import ChatMessageSchema

career = APIRouter()


@career.post("/chat/{windowId}")
async def chat_career(
    current_user: Annotated[User, Depends(get_current_active_user)],
    windowId: str,
    data: ChatMessageSchema
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")
        result = await CareerService.career_guidance(current_user, data.content, windowId)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@career.post("/generate-eq-iq-test/{windowId}")
async def generateEqIqTest(
    current_user: Annotated[User, Depends(get_current_active_user)],
    windowId: str
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")
        result = await CareerService.generate_iq_eq_test(current_user, windowId)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@career.get("/history/{windowId}")
async def get_career_history(
    current_user: Annotated[User, Depends(get_current_active_user)],
    windowId: str
):
    try:
        if current_user.onboarding is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please complete onboarding first"
            )

        result = await CareerService.get_career_history(current_user, windowId)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
