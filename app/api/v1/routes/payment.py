from fastapi import APIRouter, HTTPException
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from schemas.auth_schema import User
from schemas.payment_schema import InsertOrderSchema
from services.auth_service import AuthService
from fastapi import status, BackgroundTasks
from core.security import get_current_active_user
from pydantic import BaseModel
from services.payment_service import PaymentService

payment = APIRouter()


@payment.get("/premium-subscription-order")
async def create_premium_subscription_order(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")
        result = await PaymentService.create_premium_subscription_order(current_user)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@payment.post("/premium-subscription-order")
async def insert_premium_subscription_order_(
    current_user: Annotated[User, Depends(get_current_active_user)],
    data: InsertOrderSchema
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")
        result = await PaymentService.insert_premium_subscription_order_(current_user, data)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
