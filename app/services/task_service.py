from schemas.tasks_schema import TaskCreate
from models.tasks import TaskModel
from beanie import PydanticObjectId
from fastapi import HTTPException
import traceback

class TaskService:
    @staticmethod
    async def create_task(user_id: str, data: TaskCreate) -> dict:
        try:
            # Validate user_id format
            user_id = PydanticObjectId(user_id)

            # Create and insert task
            task = TaskModel(
                task_name=data.task_name,
                description=data.description,
                expected_duration_months=data.expected_duration_months,
                daily_hours=data.daily_hours,
                language=data.language,
                user=user_id
            )

            await task.insert()
            return {"message": "Task created successfully", "status_code": 201}

        except Exception as e:
            print(f"Error: {traceback.format_exc()}")  # Logs the full error traceback
            raise HTTPException(status_code=500, detail="Internal Server Error")
