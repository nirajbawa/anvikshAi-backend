from fastapi import APIRouter, HTTPException
import jwt
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.responses import JSONResponse
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from datetime import datetime, timedelta, timezone
from typing import Annotated
from schemas.user_schema import UserSchema
from services.auth_service import AuthService
from fastapi import status

user_auth = APIRouter()

@user_auth.post("/sign-up")
async def sign_up(data: UserSchema):
    print(data.email)
    if await AuthService.check_user_exists(data.email):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
        # return JSONResponse(status_code=400, content={"message": "User already exists"})
    try:
        result = await AuthService.create_user(data)
        print(result)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": result, "status":"true"})
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

