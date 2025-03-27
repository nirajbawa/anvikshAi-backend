from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.services.mentor_service import MentorService
from app.schemas.auth_schema import ExpertOnboardingSchema, SignInSchema, Expert, Mentor
from typing import Annotated
from app.core.security import get_current_active_user
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict


mentor = APIRouter()


@mentor.get("/allocate-mentor/{courseId}")
async def allocate(
    current_user: Annotated[Mentor, Depends(get_current_active_user)],
    courseId: str
):
    try:
        result = await MentorService.request_mentor(current_user, courseId)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


active_connections: Dict[str, WebSocket] = {}


@mentor.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    active_connections[client_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            # Expected format: "receiver_id:message"
            target_id, message = data.split(":", 1)

            if target_id in active_connections:
                await active_connections[target_id].send_text(f"From {client_id}: {message}")
            else:
                await websocket.send_text("User not found or offline.")
    except WebSocketDisconnect:
        del active_connections[client_id]
