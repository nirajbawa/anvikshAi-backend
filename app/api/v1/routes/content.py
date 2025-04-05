from fastapi import APIRouter, HTTPException, File, UploadFile
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.schemas.auth_schema import User
from fastapi import status
from app.core.security import get_current_active_user
from app.services.content_service import ContentService
from app.schemas.content_schema import ContentStatus, QuizStatus, Feedback
import PyPDF2
import io


content = APIRouter()


@content.get("/video/{dayId}")
async def get_video(
    current_user: Annotated[User, Depends(get_current_active_user)],
    dayId: str
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")
        result = await ContentService.get_video(current_user, dayId)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@content.get("/article/{dayId}")
async def get_article(
    current_user: Annotated[User, Depends(get_current_active_user)],
    dayId: str
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")
        result = await ContentService.get_article(current_user, dayId)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@content.get("/quiz/{dayId}")
async def get_quiz(
    current_user: Annotated[User, Depends(get_current_active_user)],
    dayId: str
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")
        result = await ContentService.get_quiz(current_user, dayId)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@content.get("/assignment/{dayId}")
async def get_assignment(
    current_user: Annotated[User, Depends(get_current_active_user)],
    dayId: str
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")
        result = await ContentService.get_assignment(current_user, dayId)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@content.post("/video/{dayId}")
async def set_video_status(
    current_user: Annotated[User, Depends(get_current_active_user)],
    dayId: str,
    data: ContentStatus
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")
        result = await ContentService.set_video_status(current_user, dayId, data)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@content.post("/article/{dayId}")
async def set_article_status(
    current_user: Annotated[User, Depends(get_current_active_user)],
    dayId: str,
    data: ContentStatus
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")
        result = await ContentService.set_article_status(current_user, dayId, data)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@content.post("/quiz/{dayId}")
async def set_quiz_status(
    current_user: Annotated[User, Depends(get_current_active_user)],
    dayId: str,
    data: QuizStatus
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")
        result = await ContentService.set_quiz_status(current_user, dayId, data)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@content.post("/assignment/{dayId}")
async def set_assignmnet_status(
    current_user: Annotated[User, Depends(get_current_active_user)],
    dayId: str,
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

        result = await ContentService.set_assigment_status(current_user, dayId, text)

        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@content.post("/feedback/{dayId}")
async def get_feedback(
    current_user: Annotated[User, Depends(get_current_active_user)],
    dayId: str,
    data: Feedback
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")
        result = await ContentService.get_feedback(current_user, dayId, data)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@content.get("/certificates")
async def get_certificates(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")
        result = await ContentService.get_certificates(current_user)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
@content.get("/certificate/${task_id}")
async def get_certificate(
   task_id: str,
):
    try:
        result = await ContentService.get_certificate(task_id)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        print("error : ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
