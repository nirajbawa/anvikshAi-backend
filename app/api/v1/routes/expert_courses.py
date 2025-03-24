from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from app.services.expert_courses_service import ExpertCoursesSerivce
from app.schemas.auth_schema import Expert
from app.schemas.expert_schema import ExpertCourseReviewSchema
from fastapi import BackgroundTasks
from typing import Annotated
from app.core.security import get_current_active_expert

expert_courses = APIRouter()


@expert_courses.get("/")
async def get_courses(
    current_user: Annotated[Expert, Depends(get_current_active_expert)],
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")
        result = await ExpertCoursesSerivce.get_courses(current_user, page, limit)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@expert_courses.get("/{cid}")
async def get_course(
    current_user: Annotated[Expert, Depends(get_current_active_expert)],
    cid: str
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")
        result = await ExpertCoursesSerivce.get_course(cid)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@expert_courses.post("/{cid}")
async def get_courses(
    current_user: Annotated[Expert, Depends(get_current_active_expert)],
    cid: str,
    data: ExpertCourseReviewSchema
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")
        result = await ExpertCoursesSerivce.review_course(current_user, cid, data)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
