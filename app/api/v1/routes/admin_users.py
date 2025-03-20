from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Annotated
from app.schemas.auth_schema import Admin
from app.core.security import get_current_active_admin
from app.services.admin_users_service import AdminUsersService
from fastapi.responses import JSONResponse

admin_users = APIRouter()


@admin_users.get("/")
async def get_students(
    current_user: Annotated[Admin, Depends(get_current_active_admin)],
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    try:
        result = await AdminUsersService.get_users(page, limit)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
