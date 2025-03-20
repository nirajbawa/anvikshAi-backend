from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.services.expert_auth_service import ExpertAuthSerivce
from app.schemas.auth_schema import ExpertOnboardingSchema, SignInSchema, Expert
from typing import Annotated
from app.core.security import get_current_active_expert

expert_auth = APIRouter()


@expert_auth.post("/onboarding")
async def onboarding(data: ExpertOnboardingSchema):
    try:
        result = await ExpertAuthSerivce.onboarding(data)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@expert_auth.post("/sign-in")
async def sign_in(data: SignInSchema):
    try:
        result = await ExpertAuthSerivce.sign_in(data)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@expert_auth.get("/get-current-expert")
async def get_current_user(
    current_user: Annotated[Expert, Depends(get_current_active_expert)],
):
    try:
        return current_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
