from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from app.services.user_mentor_service import UserMentorService
from app.schemas.auth_schema import User
from typing import Annotated
from app.core.security import get_current_active_user
from typing import Dict
import json
from datetime import datetime
from app.models.messages import MessageModel
import asyncio

user_mentor = APIRouter()


@user_mentor.get("/allocate-mentor/{courseId}")
async def allocate(
    current_user: Annotated[User, Depends(get_current_active_user)],
    courseId: str
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")
        result = await UserMentorService.request_mentor(current_user, courseId)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
@user_mentor.get("/{mentorId}")
async def get_mentor(
    current_user: Annotated[User, Depends(get_current_active_user)],
    mentorId: str
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")
        result = await UserMentorService.get_mentor(current_user, mentorId)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        

@user_mentor.get("/messages/{courseId}")
async def get_mentor(
    current_user: Annotated[User, Depends(get_current_active_user)],
    courseId: str
):
    try:
        if (current_user.onboarding == False):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Please complete onboarding first")
        result = await UserMentorService.get_messages(current_user, courseId)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


active_connections: Dict[str, WebSocket] = {}

@user_mentor.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Handles WebSocket connections for clients"""
    await websocket.accept()
    active_connections[client_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)  # Parse JSON data

            receiver_id = message_data.get("receiver_id")
            message = message_data.get("message")
            sender = message_data.get("sender")
            course_id =  message_data.get("course_id")
            if receiver_id and message and sender and course_id:
                # background_tasks = BackgroundTasks()
                await send_message(sender_id=client_id, receiver_id=receiver_id, message=message, sender=sender, course_id=course_id)
    except WebSocketDisconnect:
        del active_connections[client_id]

async def store_message(sender_id: str, receiver_id: str, message: str, sender: str, course_id: str):
    """Store message in MongoDB"""
    print(f"📌 Background Task: Storing message from {sender_id} to {receiver_id}: {message}")
    msg = MessageModel(sender_id=sender_id, receiver_id=receiver_id, message=message, sender=sender, timestamp=datetime.utcnow(), course_id=course_id)
    await msg.insert()

async def send_message(sender_id: str, receiver_id: str, message: str, sender:str, course_id: str):
    """Send message and store it in background"""
    if receiver_id in active_connections:
        response = {
            "sender_id": sender_id,
            "message": message,
            "sender": sender,
            "timestamp": datetime.utcnow().isoformat(),
            "course_id": course_id
        }
        await active_connections[receiver_id].send_text(json.dumps(response))

    # Store the message asynchronously in MongoDB
    # await store_message(sender_id, receiver_id, message, sender)
    asyncio.create_task(store_message(sender_id, receiver_id, message, sender, course_id))
    # background_tasks.add_task(store_message, )

