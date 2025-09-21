import google.generativeai as genai
import os
from typing import List, Dict


def init_gemini():
    genai.configure(api_key=os.getenv("AI_API_KEY"))
    return genai.GenerativeModel("gemini-2.0-flash")

def format_conversation(history: List[dict], system_prompt: str, new_message: str):
    """
    Convert history + new message into Gemini's expected format
    """
    conversation = []

    # Include system prompt in first user message
    if system_prompt:
        new_message = system_prompt + "\n" + new_message

    # Append previous messages
    for msg in history:
        conversation.append({
            "role": msg["role"],  # "user" or "assistant"
            "parts": [msg["content"]]
        })

    # Append current user message
    conversation.append({"role": "user", "parts": [new_message]})

    return conversation

def gemini_chat(conversation: List[Dict]) -> str:
    """
    Stream chat response from Gemini and return full output
    """
    try:
        model = init_gemini()
        response_stream = model.generate_content(conversation, stream=True)
        output_chunks = []
        for chunk in response_stream:
            if hasattr(chunk, "text"):
                output_chunks.append(chunk.text)
        return "".join(output_chunks)
    except Exception as e:
        return f"Error while generating response: {str(e)}"
