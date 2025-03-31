from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from app.services.mentor_service import MentorService
from app.schemas.auth_schema import User
from typing import Annotated
from app.core.security import get_current_active_mentor
from typing import Dict
import json
from datetime import datetime
from app.models.messages import MessageModel
import asyncio

mentor = APIRouter()

@mentor.get("/")
async def get_dashboard_stats(
    current_user: Annotated[User, Depends(get_current_active_mentor)]
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")
        result = await MentorService.get_dashboard(current_user)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@mentor.get("/courses")
async def get_courses(
    current_user: Annotated[User, Depends(get_current_active_mentor)]
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")
        result = await MentorService.get_courses(current_user)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@mentor.get("/messages/{courseId}")
async def get_messages(
    current_user: Annotated[User, Depends(get_current_active_mentor)],
    courseId: str
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")
        result = await MentorService.get_messages(current_user, courseId)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        