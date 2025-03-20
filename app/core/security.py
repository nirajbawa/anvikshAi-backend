from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from datetime import datetime, timedelta, timezone
from typing import Annotated
from app.models.user import UserModel
from fastapi import HTTPException, status, Depends, Header
import os
from app.schemas.auth_schema import User, TokenData, Admin, Expert
from app.models.admin import AdminModel
from app.models.expert import ExpertModel
from typing import Optional, List
from pydantic import EmailStr, Field
from beanie import PydanticObjectId

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/sign-in")


ALGORITHM = "HS256"


class UserProjection(BaseModel):
    id: Optional[PydanticObjectId] = Field(alias="_id")
    email: Optional[EmailStr]
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


class AdminProjection(BaseModel):
    id: Optional[PydanticObjectId] = Field(alias="_id")
    email: Optional[EmailStr]
    role: Optional[str]
    created_at: Optional[datetime]


class ExpertProjection(BaseModel):
    id: Optional[PydanticObjectId] = Field(alias="_id")
    email: Optional[EmailStr]
    first_name: Optional[str]
    last_name: Optional[str]
    bio: Optional[str]
    education: Optional[str]
    stream_of_education: Optional[str]
    resume: Optional[str]
    created_at: Optional[datetime]
    verified: Optional[bool]
    onboarding: Optional[bool]
    domains: Optional[List[str]]
    review_points: Optional[float]


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt_token(data: dict, secret_key: str, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, os.getenv(
            "SECRET_KEY"), algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user = await UserModel.find_one({"email": token_data.email}).project(UserProjection)
    print(user)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if not current_user.verified:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin(authorization: str = Header(None)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        if authorization is None or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid Authorization header",
            )

        # Extract the token after "Bearer "
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, os.getenv(
            "ADMIN_SECRET_KEY"), algorithms=[ALGORITHM])

        email: str = payload.get("sub")
        role: str = payload.get("role")
        if email is None or role != "admin":
            raise credentials_exception

        token_data = TokenData(email=email, role=role)
    except InvalidTokenError:
        raise credentials_exception
    user = await AdminModel.find_one({"email": token_data.email}).project(AdminProjection)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_admin(
    current_user: Annotated[Admin, Depends(get_current_admin)],
):
    return current_user


async def get_current_expert(authorization: str = Header(None)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        if authorization is None or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid Authorization header",
            )

        # Extract the token after "Bearer "
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, os.getenv(
            "EXPERT_SECRET_KEY"), algorithms=[ALGORITHM])

        email: str = payload.get("sub")
        role: str = payload.get("role")
        if email is None or role != "expert":
            raise credentials_exception

        token_data = TokenData(email=email, role=role)
    except InvalidTokenError:
        raise credentials_exception
    user = await ExpertModel.find_one({"email": token_data.email}).project(ExpertProjection)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_expert(
    current_user: Annotated[Expert, Depends(get_current_expert)],
):
    if not current_user.verified:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
