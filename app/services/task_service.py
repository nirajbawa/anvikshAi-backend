from app.schemas.tasks_schema import TaskCreate, CreateRoadmap
from app.models.tasks import TaskModel
from beanie import PydanticObjectId
from fastapi import HTTPException
import traceback
from app.core.chat_gpt import chat
from datetime import datetime, timezone, date
from app.models.user import PremiumPackage
import json
from app.models.day import DayModel
import json
from weasyprint import HTML
from fastapi.templating import Jinja2Templates
import os
import uuid
from app.models.certificates import CertificateModel
from typing import List

templates = Jinja2Templates(directory="app/certificate_template")
CERTIFICATES_DIR = "app/certificate_template"


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
                "Generate a questionnaire based on the user's task description to help create a step-by-step learning roadmap. "
                "Tailor the roadmap based on the user's educational level, stream, and preferred language to optimize their learning path.\n\n"
                f"Task: {data.description}\n"
                f"Duration: {data.expected_duration_months} months (if expected_duration_months is 0, use the user's education level to decide the timeline)\n"
                f"Daily Hours: {data.daily_hours} hours\n"
                f"Education Level: {current_user.education}\n"
                f"Education Stream: {current_user.stream_of_education}\n"
                f"Preferred Language: {current_user.language_preference}\n\n"
                f"user bio : {current_user.bio}"
                "Return the questionnaire output in the following format:\n"
                "[{'id': 'unique_id', 'question': 'Your question text', 'options': {'a': 'Option A', 'b': 'Option B', 'c': 'Option C', 'd': 'Option D'}, answer:none}]\n"
                "Ensure the questions are relevant to the task and designed to gather insights that improve the roadmap quality."
            )

            chat_response = chat(messages)

            cleaned_output = TaskService.clean_json_output(chat_response)
            questionier = json.loads(cleaned_output)

            print(questionier)

            # Create and insert task
            task = TaskModel(
                task_name=data.task_name,
                description=data.description,
                expected_duration_months=data.expected_duration_months,
                daily_hours=data.daily_hours,
                language=data.language,
                user=user_id,
                questionnaire=questionier
            )

            await task.insert()
            return {"message": "Task created successfully", "task_id": str(task.id), "questionnaire": questionier}

        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail=str(e))

    @staticmethod
    async def create_roadmap(current_user: dict, task_id: str, data: CreateRoadmap) -> dict:
        try:

            task = await TaskModel.find_one(
                {"_id": PydanticObjectId(
                    task_id), "user": PydanticObjectId(current_user.id)}
            )

            if (not task):
                raise HTTPException(
                    status_code=404,
                    detail=f"Invalid task id"
                )

            messages = (
                "You are a roadmap generator agent. Your task is to generate structured learning roadmaps based on the user's inputs. "
                "The user will provide a task description, expected duration (in months), daily study hours, and educational background, questionnaire about task description."
                "Generate a step-by-step roadmap with milestones, keeping descriptions short and focused (avoid excessive detail). "
                "Tailor the roadmap based on the user's educational level and stream to optimize their learning path.\n\n"
                f"Task: {task.description}\n"
                f"Duration: {task.expected_duration_months} months (if expected_duration_months is 0, use the user's education level to decide the timeline)\n"
                f"Daily Hours: {task.daily_hours} hours\n"
                f"Education Level: {current_user.education}\n"
                f"Education Stream: {current_user.stream_of_education}\n"
                f"Preferred Language: {current_user.language_preference}\n\n",
                f"questionnaire : {str(data.questions)}"
                f"user bio : {current_user.bio}"
                "At the end of the roadmap, provide future courses and learning suggestions on the last day."
            )

            chat_response = chat(messages)

            # Create and insert task
            # task = TaskModel(
            #     task_name=task.task_name,
            #     description=task.description,
            #     expected_duration_months=task.expected_duration_months,
            #     daily_hours=task.daily_hours,
            #     language=task.language,
            #     user=PydanticObjectId(current_user.id),
            #     questionnaire=questionier
            # )

            await task.update({
                "$set": {
                    "generated_roadmap_text": chat_response,
                    "questionnaire": data.questions
                }
            })

            return {"message": "Roadmap created successfully", "task_id": str(task.id), "roadmap": chat_response}

        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail=str(e))

    @staticmethod
    def clean_json_output(output: str) -> str:
        # Remove code block markers
        if output.startswith("```json"):
            output = output[len("```json"):].strip()
        if output.endswith("```"):
            output = output[:-3].strip()
        return output

    @staticmethod
    async def regenerate_roadmap(current_user: dict, data: str, taskId: str) -> str:

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

        task = await TaskModel.find_one(
            {"_id": PydanticObjectId(
                taskId), "user": PydanticObjectId(current_user.id)}
        )

        if (not task):
            raise HTTPException(
                status_code=404,
                detail=f"Invalid task id"
            )

        messages = (
            "You are a roadmap generator agent. Your task is to generate structured learning roadmaps based on the user's inputs. "
            "The user will provide a task description, expected duration (in months), daily study hours, and educational background, questionnaire about task description. "
            "Generate a step-by-step roadmap with milestones, keeping descriptions short and focused (avoid excessive detail). "
            "Tailor the roadmap based on the user's educational level and stream to optimize their learning path.\n\n"
            f"fix this task bsed on this data : {data}"
            f"Task: {task.description}\n"
            f"Duration: {task.expected_duration_months} months (if expected_duration_months is 0, use the user's education level to decide the timeline)\n"
            f"Daily Hours: {task.daily_hours} hours\n"
            f"Education Level: {current_user.education}\n"
            f"Education Stream: {current_user.stream_of_education}\n"
            f"Preferred Language: {current_user.language_preference}\n\n"
            f"user bio : {current_user.bio}"
            f"questionnaire : {str(task.questionnaire)}"
            "At the end of the roadmap, provide future courses and learning suggestions on the last day."
            f"previous roadmap ${task.generated_roadmap_text}"
        )

        chat_response = chat(messages)

        await task.update({
            "$set": {
                "generated_roadmap_text": chat_response
            }
        })

        return {"message": "Raodmap updated successfully", "task_id": str(task.id), "roadmap": chat_response}

    @staticmethod
    async def create_course(current_user: dict, task_id: str) -> dict:
        try:

            is_task_exists = await TaskModel.find_one(
                {"_id": PydanticObjectId(
                    task_id), "accepted": False, "user": PydanticObjectId(current_user.id)}
            )
            if (not is_task_exists):
                raise HTTPException(
                    status_code=404,
                    detail=f"Invalid task id"
                )

            messages = (
                f"You are a roadmap generator agent. Your task is to create a structured, day-by-day learning plan based on the phases of the existing roadmap: {is_task_exists.generated_roadmap_text}. "
                f"Divide the topics over {is_task_exists.expected_duration_months * 30} (if expected_duration_months is 0, use the user's education level to decide the timeline) days, considering {is_task_exists.daily_hours} hours of study per day. "
                "Include weekly milestones, review sessions, and optional practice tasks to ensure steady progress.",
                f"Daily Hours: {is_task_exists.daily_hours} hours\n"
                f"Education Level: {current_user.education}\n"
                f"Education Stream: {current_user.stream_of_education}\n"
                f"Preferred Language: {current_user.language_preference}\n\n"
                f"user bio : {current_user.bio}"
                "At the end of the roadmap, provide future courses and learning suggestions on the last day."
                "strictly Return the output only in JSON format with fields: 'day', 'topics', 'keyword' (give base keyword of the main topic to search) (in topic only mention the topic no hours or else) (dont add any extra parameter rather than day or topics in array). (make sure output is under the token limit)"
            )

            chat_response = chat(messages)
            cleaned_output = TaskService.clean_json_output(chat_response)
            day_wise_task = json.loads(cleaned_output)
            print(day_wise_task)

            day_entries = [
                DayModel(
                    day=day_data["day"],
                    topics=day_data["topics"][0],
                    status=False,
                    belongs_to=PydanticObjectId(task_id),
                    user=PydanticObjectId(current_user.id),
                    keyword=day_data["keyword"]
                )
                for day_data in day_wise_task
            ]

            # Bulk insert
            await DayModel.insert_many(day_entries)

            messages = (
                f"You are a roadmap generator agent. Your task is to analyze the given roadmap description: {is_task_exists.generated_roadmap_text}. "
                f"Identify the major phases, and strictly return them as a pure JSON array like this: "
                f'[{{"topic": "title", "description": "in one line"}}]'
            )
            chat_response = chat(messages)
            cleaned_output = TaskService.clean_json_output(chat_response)
            roadmap_phases = json.loads(cleaned_output)

            await is_task_exists.update({
                "$set": {
                    "roadmap_phases": roadmap_phases,
                    "accepted": True
                }
            })

            return {"message": "Course created successfully"}

        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail=str(e))

    @staticmethod
    async def get_tasks(current_user: dict) -> dict:
        try:

            is_task_exists = await TaskModel.find(
                {"accepted": True, "user": PydanticObjectId(current_user.id)}
            ).to_list()

            if (not is_task_exists):
                raise HTTPException(
                    status_code=404,
                    detail=f"No task exists"
                )

            data = [json.loads(task.model_dump_json())
                    for task in is_task_exists]

            return {"message": "Tasks fetched successfully", "data": data}

        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail="Internal Server Error")

    @staticmethod
    async def get_task(current_user: dict, taskId: str) -> dict:
        try:

            is_task_exists = await TaskModel.find_one(
                {"_id": PydanticObjectId(
                    taskId), "accepted": True, "user": PydanticObjectId(current_user.id)}
            )

            if (not is_task_exists):
                raise HTTPException(
                    status_code=404,
                    detail=f"No task exists"
                )

            data = json.loads(is_task_exists.model_dump_json())
            return {"message": "Task fetched successfully", "data": data}

        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail=str(e))

    @staticmethod
    async def task_progress(current_user: dict, taskId: str) -> dict:
        try:

            is_task_exists = await TaskModel.find_one(
                {"_id": PydanticObjectId(
                    taskId), "accepted": True, "user": PydanticObjectId(current_user.id)}
            )

            if (not is_task_exists):
                raise HTTPException(
                    status_code=404,
                    detail=f"No task exists"
                )

            completed_days = await DayModel.find_one(
                {"belongs_to": PydanticObjectId(
                    taskId), "status": True, "user": PydanticObjectId(current_user.id)}
            ).count()

            total_days = await DayModel.find_one(
                {"belongs_to": PydanticObjectId(
                    taskId), "user": PydanticObjectId(current_user.id)}
            ).count()

            if total_days == completed_days:

                task = await TaskModel.find_one({
                    "_id": PydanticObjectId(taskId)
                })

                pdf_path = TaskService.generate_certificate({
                    "name": current_user.first_name + " " + current_user.last_name,
                    "course": task.task_name,
                })

                print(pdf_path)

                certificate = CertificateModel(
                    task_id=PydanticObjectId(taskId),
                    user=PydanticObjectId(current_user.id),
                    task_name=task.task_name,
                    link=pdf_path
                )

                await certificate.insert()

                await task.update({
                    "$set": {
                        "completed": True
                    }
                })

            data = {
                "completed_days": completed_days,
                "total_days": total_days
            }

            return {"message": "Task progess fetched successfully", "data": data}

        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail=str(e))

    @staticmethod
    def generate_certificate(data: dict):
        # Fill in the template with user data
        today_date = date.today().strftime("%B %d, %Y")
        template = templates.get_template(
            "certificate.html")
        unique_id = str(uuid.uuid4())[:8]  # Shorten the UUID for readability

        html_content = template.render(
            name=data["name"], course=data["course"], certificate_id=unique_id, instructor="AiNigma", date=today_date)

        # Convert HTML to PDF
        file_name = f"{data['name'].replace(' ', '_')}_{unique_id}_certificate.pdf"
        pdf_path = os.path.join(CERTIFICATES_DIR, file_name)
        HTML(string=html_content).write_pdf(pdf_path)
        return pdf_path
