from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Annotated
from app.schemas.auth_schema import Admin
from app.core.security import get_current_active_admin
from app.services.admin_expert_service import AdminExpertService
from fastapi.responses import JSONResponse
from app.schemas.auth_schema import ExpertInviteSchema
from fastapi import BackgroundTasks

admin_expert = APIRouter()


@admin_expert.post("/")
async def invite_expert(
    current_user: Annotated[Admin, Depends(get_current_active_admin)],
    background_tasks: BackgroundTasks,
    data: ExpertInviteSchema
):
    try:
        result = await AdminExpertService.invite_expert(data, background_tasks)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@admin_expert.get("/")
async def get_experts(
    current_user: Annotated[Admin, Depends(get_current_active_admin)],
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    try:
        result = await AdminExpertService.get_experts(page, limit)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
