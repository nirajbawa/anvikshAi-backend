from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from app.services.admin_courses_service import AdminCoursesSerivce
from app.schemas.auth_schema import Expert
from app.schemas.expert_schema import ExpertCourseReviewSchema
from fastapi import BackgroundTasks
from typing import Annotated
from app.core.security import get_current_active_admin

admin_courses = APIRouter()


@admin_courses.get("/")
async def get_courses(
    current_user: Annotated[Expert, Depends(get_current_active_admin)],
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    try:
        result = await AdminCoursesSerivce.get_courses(page, limit)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
