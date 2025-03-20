from fastapi import HTTPException, Query
from app.models.user import UserModel
import json
import math
from typing import Optional
from pydantic import EmailStr, Field
from datetime import datetime
from pydantic import BaseModel
from beanie import PydanticObjectId


class UserProjection(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    dob: Optional[datetime]
    bio: Optional[str]
    education: Optional[str]  # Assuming it's a string for simplicity
    stream_of_education: Optional[str]
    language_preference: Optional[str]
    verified: bool
    onboarding: bool
    premium_package: Optional[str]  # Assuming it's a string for simplicity
    validTill: Optional[datetime]
    razorpay_order_id: Optional[str]
    created_at: Optional[datetime]


class AdminUsersService:
    @staticmethod
    async def get_users(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)) -> dict:
        try:
            # Count total users
            total_users = await UserModel.find().count()

            if total_users == 0:
                raise HTTPException(status_code=404, detail="No users found")

            # Calculate pagination values
            skip = (page - 1) * limit
            total_pages = math.ceil(total_users / limit)

            # Fetch users with pagination
            users = await UserModel.find().project(UserProjection).skip(skip).limit(limit).to_list()

            # Exclude password from response
            data = [
                {key: value for key, value in json.loads(
                    user.model_dump_json()).items() if key != "password"}
                for user in users
            ]

            return {
                "message": "Data fetched successfully",
                "total_users": total_users,
                "total_pages": total_pages,
                "current_page": page,
                "users": data
            }

        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=str(e))
