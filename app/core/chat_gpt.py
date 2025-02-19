from pydantic import BaseModel
import ollama

def chat(data: list):
    try:
        
        response = ollama.chat(
            model="deepseek-r1:1.5b",
            messages=data,
        )
        return response["message"]["content"]
    except Exception as e:
        return {"error": str(e)}
