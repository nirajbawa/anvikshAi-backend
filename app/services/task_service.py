from schemas.tasks_schema import TaskCreate
from models.tasks import TaskModel
from beanie import PydanticObjectId
from fastapi import HTTPException
import traceback
from core.chat_gpt import chat


class TaskService:
    @staticmethod
    async def create_task(user_id: str, data: TaskCreate) -> dict:
        try:
            # Validate user_id format
            user_id = PydanticObjectId(user_id)

            messages = [
                {"role": "system",
                 "content": "You are a roadmap generator agent. Your task is to generate structured learning roadmaps based on the user's inputs. The user will provide a task description, expected duration (in months), and daily study hours. Generate a step-by-step roadmap with milestones, weekly goals, and necessary resources."},
                {"role": "user", "content": f"Task: {data.description}\n"
                 f"Duration: {data.expected_duration_months} months\n"
                 f"Daily Hours: {data.daily_hours} hours"}
            ]
            
            chat_response = chat(messages)
            
            
            print("response roadmap : ")
            print(chat_response)
        

            # Create and insert task
            task = TaskModel(
                task_name=data.task_name,
                description=data.description,
                expected_duration_months=data.expected_duration_months,
                daily_hours=data.daily_hours,
                language=data.language,
                user=user_id,
                generated_roadmap_text=chat_response
            )

            await task.insert()
            return {"message": "Task created successfully", "roadmap": chat_response, "status_code": 201}

        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail="Internal Server Error")

    @staticmethod
    async def create_roadmap(message) -> dict | Exception:
        pass
