from typing import List, Dict
from app.models.chatHistory import ChatMessage
from datetime import datetime, timezone

async def save_message(user_id: str, window_id: str, content: str, role: str):
    message_obj = {"role": role, "content": content}

    chat_doc = await ChatMessage.find_one(
        ChatMessage.user_id == user_id,
        ChatMessage.window_id == window_id
    )

    if chat_doc:
        chat_doc.messages.append(message_obj)
        await chat_doc.save()
    else:
        chat_doc = ChatMessage(user_id=user_id, window_id=window_id, messages=[message_obj])
        await chat_doc.insert()


async def get_chat_history(user_id: str, window_id: str) -> List[Dict]:
    chat_doc = await ChatMessage.find_one(
        ChatMessage.user_id == user_id,
        ChatMessage.window_id == window_id
    )
    if chat_doc:
        return chat_doc.messages
    return []