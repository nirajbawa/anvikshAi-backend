from fastapi import HTTPException
import traceback
from app.models.videos import VideoModel
from app.models.articles import ArticleModel
from app.models.assignments import AssignmentModel
from app.models.quizzes import QuizModel
from app.models.day import DayModel
from app.models.certificates import CertificateModel
from beanie import PydanticObjectId
import json
from app.schemas.content_schema import ContentStatus, QuizStatus
from app.core.chat_gpt import chat
from app.services.task_service import TaskService


class ContentService:
    @staticmethod
    async def get_video(current_user: dict, day_id: str) -> dict:
        try:
            is_task_exists = await VideoModel.find_one(
                {"day": PydanticObjectId(
                    day_id), "user": PydanticObjectId(current_user.id)}
            )
            if (not is_task_exists):
                raise HTTPException(
                    status_code=404,
                    detail=f"Invalid day id"
                )

            data = json.loads(is_task_exists.model_dump_json())

            return {"message": "Day fetched successfully", "data": data}

        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail="Internal Server Error")

    @staticmethod
    async def get_article(current_user: dict, day_id: str) -> dict:
        try:
            is_task_exists = await ArticleModel.find_one(
                {"day": PydanticObjectId(
                    day_id), "user": PydanticObjectId(current_user.id)}
            )
            if (not is_task_exists):
                raise HTTPException(
                    status_code=404,
                    detail=f"Invalid day id"
                )

            data = json.loads(is_task_exists.model_dump_json())

            return {"message": "Day fetched successfully", "data": data}

        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail="Internal Server Error")

    @staticmethod
    async def get_assignment(current_user: dict, day_id: str) -> dict:
        try:
            is_task_exists = await AssignmentModel.find_one(
                {"day": PydanticObjectId(
                    day_id), "user": PydanticObjectId(current_user.id)}
            )
            if (not is_task_exists):
                raise HTTPException(
                    status_code=404,
                    detail=f"Invalid day id"
                )

            data = json.loads(is_task_exists.model_dump_json())

            return {"message": "Day fetched successfully", "data": data}

        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail="Internal Server Error")

    @staticmethod
    async def get_quiz(current_user: dict, day_id: str) -> dict:
        try:
            is_task_exists = await QuizModel.find_one(
                {"day": PydanticObjectId(
                    day_id), "user": PydanticObjectId(current_user.id)}
            )
            if (not is_task_exists):
                raise HTTPException(
                    status_code=404,
                    detail=f"Invalid day id"
                )

            data = json.loads(is_task_exists.model_dump_json())

            filter_questions = []

            for question in data["questions"]:
                filter_questions.append({
                    "id": question["id"],
                    "question": question["question"],
                    "options": question["options"],
                })

            filltered_data = {
                "id": data["id"],
                "questions": filter_questions,
                "day": data["day"],
                "user": data["user"],
                "created_at": data["created_at"],
                "quiz_completed": data["quiz_completed"],
                "marks": data["marks"]
            }

            return {"message": "Day fetched successfully", "data": filltered_data}

        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail="Internal Server Error")

    @staticmethod
    async def set_video_status(current_user: dict, day_id: str, data: ContentStatus) -> dict:
        try:
            is_task_exists = await VideoModel.find_one(
                {"day": PydanticObjectId(day_id),
                 "user": PydanticObjectId(current_user.id)
                 }
            )
            if (not is_task_exists):
                raise HTTPException(
                    status_code=404,
                    detail=f"Invalid day id"
                )

            day = await DayModel.find_one({
                "_id": PydanticObjectId(day_id),
                "user": PydanticObjectId(current_user.id)
            })

            if (not day):
                raise HTTPException(
                    status_code=404,
                    detail=f"Invalid day id"
                )

            feedback = await ContentService.generate_feedback(
                day.feedback, f"task name : watch suggested videos about{str(day.topics)}", data.status, f"{data.marks}/10")

            await day.update({
                "$set": {
                    "feedback": feedback
                }
            })

            await is_task_exists.update({
                "$set": {
                    "marks": data.marks,
                    "all_video_completed": data.status
                }
            })

            data = json.loads(is_task_exists.model_dump_json())

            return {"message": "Video updated successfully", "data": data}

        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail="Internal Server Error")

    @staticmethod
    async def set_article_status(current_user: dict, day_id: str, data: ContentStatus) -> dict:
        try:
            is_task_exists = await ArticleModel.find_one(
                {"day": PydanticObjectId(day_id),
                 "user": PydanticObjectId(current_user.id)
                 }
            )
            if (not is_task_exists):
                raise HTTPException(
                    status_code=404,
                    detail=f"Invalid day id"
                )

            day = await DayModel.find_one({
                "_id": PydanticObjectId(day_id),
                "user": PydanticObjectId(current_user.id)
            })

            if (not day):
                raise HTTPException(
                    status_code=404,
                    detail=f"Invalid day id"
                )

            feedback = await ContentService.generate_feedback(
                day.feedback, f"task name :  read suggeted topics about {str(day.topics)}", data.status, f"{data.marks}/10")

            await day.update({
                "$set": {
                    "feedback": feedback
                }
            })

            await is_task_exists.update({
                "$set": {
                    "marks": data.marks,
                    "all_article_readed": data.status
                }
            })

            data = json.loads(is_task_exists.model_dump_json())

            return {"message": "Article updated successfully", "data": data}

        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail="Internal Server Error")

    @staticmethod
    def get_question(id: int, data: list):
        for current_question in data:
            if current_question["id"] == id:
                return current_question
        return None

    @staticmethod
    async def set_quiz_status(current_user: dict, day_id: str, data: QuizStatus) -> dict:
        try:
            is_quiz_exists = await QuizModel.find_one(
                {"day": PydanticObjectId(day_id),
                 "user": PydanticObjectId(current_user.id),
                 }
            )
            if (not is_quiz_exists):
                raise HTTPException(
                    status_code=404,
                    detail=f"Invalid day id"
                )

            filter_data = json.loads(is_quiz_exists.model_dump_json())
            score = 0

            for current_question in data.questions:
                question = ContentService.get_question(
                    current_question["id"], filter_data["questions"])
                if question:
                    if (current_question["answer"] == question["answer"]):
                        score += 1

            result = {
                "marks": score,
                "total_questions": len(filter_data["questions"]),
                "percentage": (score / len(filter_data["questions"])) * 100,
            }

            day = await DayModel.find_one({
                "_id": PydanticObjectId(day_id),
                "user": PydanticObjectId(current_user.id)
            })

            if (not day):
                raise HTTPException(
                    status_code=404,
                    detail=f"Invalid day id"
                )

            feedback = await ContentService.generate_feedback(
                day.feedback, f"task name : solve suggested quiz based on {str(day.topics)}", True, f"{score}/10")

            await day.update({
                "$set": {
                    "feedback": feedback
                }
            })

            await is_quiz_exists.update({
                "$set": {
                    "marks": score,
                    "quiz_completed": True
                }
            })

            return {"message": "Quiz updated successfully", "data": filter_data, "result": result}

        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail="Internal Server Error")

    @staticmethod
    async def set_assigment_status(current_user: dict, day_id: str, assignment: str) -> dict:
        try:
            is_assign_exists = await AssignmentModel.find_one(
                {"day": PydanticObjectId(day_id),
                 "user": PydanticObjectId(current_user.id),
                 }
            )
            if (not is_assign_exists):
                raise HTTPException(
                    status_code=404,
                    detail=f"Invalid day id"
                )

            data = json.loads(is_assign_exists.model_dump_json())

            messages = (
                f"You are an assignment checker agent. Your task is to analyze the given question and evaluate the provided assignment. "
                f"question : {is_assign_exists.assinments_question}"
                f"submition: {assignment}"
                f"Assign marks out of 10 based on the quality and completeness of the answer. "
                f"Strictly return the output in pure JSON format, like this: {{\"marks\": int}}"
            )

            chat_response = chat(messages)
            print(chat_response)
            cleaned_output = TaskService.clean_json_output(chat_response)
            chat_out = json.loads(cleaned_output)

            day = await DayModel.find_one({
                "_id": PydanticObjectId(day_id),
                "user": PydanticObjectId(current_user.id)
            })

            if (not day):
                raise HTTPException(
                    status_code=404,
                    detail=f"Invalid day id"
                )

            feedback = await ContentService.generate_feedback(
                day.feedback, f"task name : solve suggested assignment based on {str(day.topics)}", True, f"{chat_out['marks']}/10")

            await day.update({
                "$set": {
                    "feedback": feedback
                }
            })

            await is_assign_exists.update({
                "$set": {
                    "marks": chat_out["marks"],
                    "assinments_completed": True
                }
            })

            return {"message": "assginment updated successfully", "data": data, "marks": chat_out["marks"]}

        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail="Internal Server Error")

    @staticmethod
    async def get_feedback(current_user: dict, day_id, data: str) -> dict:
        try:
            day = await DayModel.find_one({
                "_id": PydanticObjectId(day_id),
                "user": PydanticObjectId(current_user.id)
            })

            if (not day):
                raise HTTPException(
                    status_code=404,
                    detail=f"Invalid day id"
                )

            messages = (
                "You are a roadmap chat agent. Your task is to analyze the given data, provide feedback, and answer the user's query. "
                "Consider the following details: "
                f"- Previous feedback about their task performance: {str(day.feedback)}\n"
                f"- Previous user task scores: {str(data)}\n"
                "Strictly return the output in pure JSON format, like this: {\"answer\": \"your answer here\"}"
            )

            chat_response = chat(messages)
            cleaned_output = TaskService.clean_json_output(chat_response)
            chat_out = json.loads(cleaned_output)

            return {"message": "feedback successfully", "data": chat_out}

        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail="Internal Server Error")

    @staticmethod
    async def generate_feedback(previous_feedback: str, task_name, task_status, task_score) -> str:
        try:
            messages = (
                f"You are an assignment feedback agent. Your task is to analyze the given data and provide feedback. "
                f"Consider the following details: "
                f"Previous feedback: {str(previous_feedback)} "
                f"Name of task: {str(task_name)} "
                f"Status of task: {str(task_status)} "
                f"Score of task: {str(task_score)} "
                f"Strictly Return the output in pure JSON format, like this: {{\"feedback\": \"Your feedback here (only str)\"}}"
            )

            chat_response = chat(messages)
            cleaned_output = TaskService.clean_json_output(chat_response)
            chat_out = json.loads(cleaned_output)

            return chat_out["feedback"]
        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail="Internal Server Error")

    @staticmethod
    async def get_certificates(current_user: dict) -> dict:
        try:
            is_task_exists = await CertificateModel.find(
                {"user": PydanticObjectId(current_user.id)}
            ).to_list()

            if (not is_task_exists):
                raise HTTPException(
                    status_code=404,
                    detail=f"No task exists"
                )

            data = [json.loads(task.model_dump_json())
                    for task in is_task_exists]
            return {"message": "Certificates fetched successfully", "data": data}
        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail=str(e))
