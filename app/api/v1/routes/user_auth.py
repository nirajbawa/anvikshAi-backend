from fastapi import APIRouter, HTTPException
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.schemas.auth_schema import SignUpSchema, VerifyOTPSchema, SignInSchema, User, Onboarding
from app.services.auth_service import AuthService
from fastapi import status, BackgroundTasks
from app.core.security import get_current_active_user
from fastapi.security import OAuth2PasswordRequestForm

user_auth = APIRouter()


@user_auth.post("/sign-up")
async def sign_up(data: SignUpSchema, background_tasks: BackgroundTasks):
    if await AuthService.check_user_exists(data.email):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User already exists")
    try:
        result = await AuthService.create_user(data, background_tasks)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": result,  "status": True})
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@user_auth.post("/verify")
async def verify(data: VerifyOTPSchema):
    if await AuthService.check_user_exists(data.email):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User already exists")
    try:
        result = await AuthService.verify_otp(data.email, data.otp)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@user_auth.post("/sign-in")
async def sign_in(data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    try:

        result = await AuthService.sign_in(data)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@user_auth.get("/get-current-user")
async def get_current_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    try:
        return current_user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@user_auth.get("/onboarding")
async def is_onboarding_completed(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    try:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "on boarding is status", "data": {"onboarding": current_user.onboarding}})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@user_auth.post("/onboarding")
async def onboarding(
    current_user: Annotated[User, Depends(get_current_active_user)],
    data:  Onboarding
):
    try:
        result = await AuthService.onboarding(current_user.email, data)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": result,  "status": True})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


