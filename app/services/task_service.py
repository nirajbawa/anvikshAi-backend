from schemas.tasks_schema import TaskCreate, TaskAccept
from models.tasks import TaskModel
from beanie import PydanticObjectId
from fastapi import HTTPException
import traceback
from core.chat_gpt import chat
from datetime import datetime, timedelta, timezone
from models.user import PremiumPackage
import json


class TaskService:
    @staticmethod
    async def is_subscription_active(user: dict) -> bool:
        try:
            if user.validTill:
                # Convert to timezone-aware datetime (if naive)
                if user.validTill.tzinfo is None:
                    user.validTill = user.validTill.replace(
                        tzinfo=timezone.utc)

                # Compare with current UTC time
                if user.validTill > datetime.now(timezone.utc):
                    return True

        except Exception as e:
            print(f"Error checking subscription: {e}")
        return False

    @staticmethod
    async def can_create_task(user: dict) -> tuple[bool, int, int]:
        current_month = datetime.now(timezone.utc).month
        current_year = datetime.now(timezone.utc).year

        # Set task limits based on subscription plan
        task_limits = {
            PremiumPackage.BASIC: 4,
            PremiumPackage.PREMIUM: 10
        }

        max_tasks = task_limits.get(user.premium_package, 4)

        # Count tasks created this month
        task_count = await TaskModel.find(
            {
                "user": user.id,
                "created_at": {"$gte": datetime(current_year, current_month, 1, tzinfo=timezone.utc)}
            }
        ).count()

        return task_count < max_tasks, task_count, max_tasks

    @staticmethod
    async def create_task(current_user: dict, data: TaskCreate) -> dict:
        try:

            # Validate user_id format
            user_id = PydanticObjectId(current_user.id)

            # Check if subscription is active
            if not await TaskService.is_subscription_active(current_user):
                raise HTTPException(
                    status_code=403,
                    detail="Your subscription has expired. Please renew to continue creating tasks."
                )

            can_create, current_tasks, max_tasks = await TaskService.can_create_task(current_user)

            if not can_create:
                raise HTTPException(
                    status_code=403,
                    detail=f"You've reached your task limit for this month ({current_tasks}/{max_tasks} tasks). Upgrade your plan for more tasks."
                )

            messages = (
                "You are a roadmap generator agent. Your task is to generate structured learning roadmaps based on the user's inputs. "
                "The user will provide a task description, expected duration (in months), daily study hours, and educational background. "
                "Generate a step-by-step roadmap with milestones, weekly goals. Tailor the roadmap based on the user's educational level and stream to optimize their learning path.\n\n"
                f"Task: {data.description}\n"
                f"Duration: {data.expected_duration_months} months\n"
                f"Daily Hours: {data.daily_hours} hours\n"
                f"Education Level: {current_user.education}\n"
                f"Education Stream: {current_user.stream_of_education}\n"
                f"Language Preference: {current_user.language_preference}"
            )
            chat_response = chat(messages)

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
            return {"message": "Task created successfully", "task_id": str(task.id), "roadmap": chat_response}

        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail="Internal Server Error")

    @staticmethod
    def clean_json_output(output: str) -> str:
        # Remove code block markers
        if output.startswith("```json"):
            output = output[len("```json"):].strip()
        if output.endswith("```"):
            output = output[:-3].strip()
        return output

    @staticmethod
    async def accept_task(current_user: dict, data: TaskAccept, task_id: str) -> dict:
        try:

            is_task_exists = await TaskModel.find_one(
                {"_id": PydanticObjectId(
                    task_id), "accepted": False, "user": PydanticObjectId(current_user.id)}
            )
            print(is_task_exists)
            if (not is_task_exists):
                raise HTTPException(
                    status_code=404,
                    detail=f"Invalid task id"
                )

            messages = (
                f"You are a roadmap generator agent. Your task is to create a structured, day-by-day learning plan based on the phases of the existing roadmap: {is_task_exists.generated_roadmap_text}. "
                f"Divide the topics over {is_task_exists.expected_duration_months * 30} days, considering {is_task_exists.daily_hours} hours of study per day. "
                "Include weekly milestones, review sessions, and optional practice tasks to ensure steady progress.",
                "Return the output in JSON format with fields: 'day', 'topics', 'status:'false'. (make sure output is under the token limit)"
            )

            chat_response = chat(messages)

            print(chat_response)
            cleaned_output = TaskService.clean_json_output(chat_response)
            day_wise_task = json.loads(cleaned_output)

            await is_task_exists.update({
                "$set": {
                    "day_wise_tasks": day_wise_task,
                    "accepted": True
                }
            })

            return {"message": "Task created successfully", "status_code": 200}

        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail="Internal Server Error")
