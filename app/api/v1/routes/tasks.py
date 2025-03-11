from fastapi import APIRouter, HTTPException, File, UploadFile
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse
from app.schemas.auth_schema import User
from fastapi import status
from app.core.security import get_current_active_user
from app.schemas.tasks_schema import TaskCreate, TaskAccept, UpdateDay, ModifyTask
from app.services.task_service import TaskService
from app.services.day_n_task_service import DayNTaskSerivce
import os
import PyPDF2
import io


task = APIRouter()

CERTIFICATES_DIR = "app/certificate_template"


@task.post("/create-task")
async def create_task(
    current_user: Annotated[User, Depends(get_current_active_user)],
    data: TaskCreate
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")
        result = await TaskService.create_task(current_user, data)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@task.post("/accept-task/{task_id}")
async def accept_task(
    current_user: Annotated[User, Depends(get_current_active_user)],
    task_id: str,
    data: TaskAccept
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")

        result = await TaskService.accept_task(current_user, data, task_id)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@task.post("/accept-task-modify/{task_id}")
async def modify_task(
    current_user: Annotated[User, Depends(get_current_active_user)],
    task_id: str,
    data: ModifyTask
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")

        result = await TaskService.regenerate_task(current_user, data.text, task_id)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@task.post("/create-day-{dayn}-task-{task_id}")
async def create_d_n_task(
    current_user: Annotated[User, Depends(get_current_active_user)],
    dayn: str,
    task_id: str
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")
        print("hello")
        result = await DayNTaskSerivce.create_day_n_task(current_user, dayn, task_id)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@task.get("/")
async def get_tasks(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")

        result = await TaskService.get_tasks(current_user)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@task.get("/{taskId}")
async def get_task(
    current_user: Annotated[User, Depends(get_current_active_user)],
    taskId: str
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")

        result = await TaskService.get_task(current_user, taskId)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@task.get("/days/{taskId}")
async def get_days(
    current_user: Annotated[User, Depends(get_current_active_user)],
    taskId: str
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")

        result = await DayNTaskSerivce.get_days(current_user, taskId)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@task.get("/day/{taskId}/{dayId}")
async def get_day(
    current_user: Annotated[User, Depends(get_current_active_user)],
    taskId: str,
    dayId: str
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")

        result = await DayNTaskSerivce.get_day(current_user, taskId, dayId)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@task.patch("/day/{taskId}/{dayId}")
async def update_day(
    current_user: Annotated[User, Depends(get_current_active_user)],
    taskId: str,
    dayId: str,
    data: UpdateDay
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")

        result = await DayNTaskSerivce.update_day(current_user, taskId, dayId)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@task.get("/task-progress/{taskId}")
async def task_progress(
    current_user: Annotated[User, Depends(get_current_active_user)],
    taskId: str
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")

        result = await TaskService.task_progress(current_user, taskId)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@task.get("/download-certificate/{filename}", )
async def download_certificate(current_user: Annotated[User, Depends(get_current_active_user)], filename: str):
    file_path = os.path.join(CERTIFICATES_DIR, filename)

    # Check if file exists
    if not os.path.exists(file_path):
        return {"error": "File not found"}

    # Serve the PDF
    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=filename
    )


@task.post("/readpdf")
async def pdf_reader(
    current_user: Annotated[User, Depends(get_current_active_user)],
    file: UploadFile = File(...),
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")

        contents = await file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(contents))

        # Extract text from each page
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        print(text)

        return JSONResponse(status_code=status.HTTP_200_OK, content={"text": text})
    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
