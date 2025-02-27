from fastapi import APIRouter, HTTPException
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from schemas.auth_schema import User
from fastapi import status
from core.security import get_current_active_user
from schemas.tasks_schema import TaskCreate, TaskAccept
from services.task_service import TaskService


task = APIRouter()


@task.post("/create-task")
async def create_task(
    current_user: Annotated[User, Depends(get_current_active_user)],
    data: TaskCreate
):
    try:
        if (current_user.onboarding == False):
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please complete onboarding first")
        result = await TaskService.create_task(current_user, data)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

    except Exception as e:
        print("error : ", e)
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@task.post("/accept-task/{task_id}")
async def accept_task(
    current_user: Annotated[User, Depends(get_current_active_user)],
    task_id: str,
    data: TaskAccept
):
    try:
        print(task_id)
        if (current_user.onboarding == False):
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please complete onboarding first")

        result = await TaskService.accept_task(current_user, data, task_id)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        print("error : ", e)
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
