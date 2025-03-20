from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.services.admin_auth_service import AdminAuthService
from app.schemas.auth_schema import SignInSchema, VerifyOTPSchema, Admin
from fastapi import BackgroundTasks
from typing import Annotated
from app.core.security import get_current_active_admin


admin_auth = APIRouter()


@admin_auth.post("/sign-in")
async def sign_up(data: SignInSchema, background_tasks: BackgroundTasks):
    try:
        result = await AdminAuthService.sign_in(data, background_tasks)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@admin_auth.post("/verify")
async def verify(data: VerifyOTPSchema):
    try:
        print(data)
        result = await AdminAuthService.verify_otp(data.email, data.otp)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@admin_auth.get("/get-current-user")
async def get_current_user(
    current_user: Annotated[Admin, Depends(get_current_active_admin)],
):
    try:
        return current_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
