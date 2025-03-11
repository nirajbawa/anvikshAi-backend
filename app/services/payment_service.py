from fastapi import HTTPException, BackgroundTasks
import traceback
import razorpay
import os
from beanie import PydanticObjectId
from models.user import UserModel
from datetime import datetime, timezone, timedelta

client = razorpay.Client(
    auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET")))


class PaymentService:
    @staticmethod
    async def create_premium_subscription_order(current_user: dict) -> str:
        try:
            amount = float(500) * 100
            data = client.order.create({
                "amount": amount,
                "currency": "INR",
                "notes": {
                    "user": str(current_user.id),
                }
            })
            print(data)
            return {"message": "Order created successfully", "data": data}

        except Exception as e:
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def insert_premium_subscription_order_(current_user: dict, data: dict) -> str:
        try:
            is_task_exists = await UserModel.find_one(
                {"_id": PydanticObjectId(
                    current_user.id)
                 }
            )
            if (not is_task_exists):
                raise HTTPException(
                    status_code=404,
                    detail=f"Invalid user id"
                )

            plan_expiry_date = datetime.now(timezone.utc) + timedelta(days=30)

            await is_task_exists.update({
                "$set": {
                    "razorpay_order": data.razorpay_order_id,
                    "validTill": plan_expiry_date,
                    "premium_package": "Premium"
                }
            })

            return {"message": "Order inserted successfully"}

        except Exception as e:
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=str(e))
