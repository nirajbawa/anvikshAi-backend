from fastapi import HTTPException
import traceback
from core.chat_gpt import chat
from beanie import PydanticObjectId
from models.day import DayModel
from core.chat_gpt import chat
from services.task_service import TaskService
import json
from models.videos import VideoModel
from models.articles import ArticleModel
from models.assignments import AssignmentModel
from models.quizzes import QuizModel


class DayNTaskSerivce:
    @staticmethod
    async def create_day_n_task(current_user: dict, dayn: str, task_id: str) -> dict:
        try:
            is_day_exists = await DayModel.find_one({
                "_id": PydanticObjectId(dayn),
                "belongs_to": PydanticObjectId(task_id),
                "content": False,
                "user": PydanticObjectId(current_user.id)
            })

            if (not is_day_exists):
                raise HTTPException(
                    status_code=404,
                    detail=f"Invalid day id"
                )

            day_description_and_tasks = await DayNTaskSerivce.create_task_description(is_day_exists.topics)
            video_content = await DayNTaskSerivce.create_video_list(str(day_description_and_tasks["topics"]))
            article_content = await DayNTaskSerivce.create_article_list(str(day_description_and_tasks["topics"]))
            assignment_content = await DayNTaskSerivce.create_assignment(str(day_description_and_tasks["topics"]))
            quiz_content = await DayNTaskSerivce.create_quiz(str(day_description_and_tasks["topics"]))

            video = VideoModel(
                videos_list=video_content,
                day=PydanticObjectId(dayn),
                user=PydanticObjectId(current_user.id)
            )

            await video.insert()

            article = ArticleModel(
                articles_list=article_content,
                day=PydanticObjectId(dayn),
                user=PydanticObjectId(current_user.id)
            )

            await article.insert()

            assignment = AssignmentModel(
                assinments_question=assignment_content["assignment_question"],
                day=PydanticObjectId(dayn),
                user=PydanticObjectId(current_user.id)
            )

            await assignment.insert()

            quiz = QuizModel(
                questions=quiz_content,
                day=PydanticObjectId(dayn),
                user=PydanticObjectId(current_user.id)
            )

            await quiz.insert()

            await is_day_exists.update({
                "$set": {
                    "description": day_description_and_tasks["description"],
                    "leaning_topics": day_description_and_tasks["topics"],
                    "video": PydanticObjectId(video.id),
                    "quiz": PydanticObjectId(quiz.id),
                    "assignment": PydanticObjectId(assignment.id),
                    "articles": PydanticObjectId(article.id),
                    "content": True
                }
            })

            return {"message": "Day n task created successfully"}

        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail=str(e))

    @staticmethod
    async def create_task_description(topics: str) -> dict:
        try:
            messages = (
                f"You are a roadmap generator agent. Your task is to analyze the given day's topics: {topics}. "
                f"Based on the topics, generate a short and precise description of the day and list only the relevant subtopics covered. "
                f"Do not include any unnecessary or irrelevant topics. Return the output in valid JSON format like this: "
                '{"description": "", "topics": []}'
            )

            chat_response = chat(messages)
            cleaned_output = TaskService.clean_json_output(chat_response)
            data = json.loads(cleaned_output)

            # print(data)
            return data
        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail=str(e))

    @staticmethod
    async def create_video_list(topics: str) -> dict:
        try:
            messages = (
                f"You are a roadmap generator agent. Your task is to analyze the given day's topics: {topics}. "
                f"Based on the topics, generate the best video content list from YouTube for learning these topics. "
                f"Ensure no duplicate video for the same topic. "
                f"Return the output strictly in pure JSON format, like this: "
                f'[{{"topic": "", "link": ""}}]'
            )

            chat_response = chat(messages)
            cleaned_output = TaskService.clean_json_output(chat_response)
            data = json.loads(cleaned_output)

            # print(chat_response)
            return data
        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail=str(e))

    @staticmethod
    async def create_article_list(topics: str) -> dict:
        try:
            messages = (
                f"You are a roadmap generator agent. Your task is to analyze the given day's topics: {topics}. "
                f"Based on the topics, generate a list of the best learning articles from reliable sources. "
                f"Ensure no duplicate articles for the same topic. "
                f"Return the output in pure JSON format, like this: "
                f'[{{"topic": "topic_name", "link": "article_link"}}]'
            )

            chat_response = chat(messages)
            cleaned_output = TaskService.clean_json_output(chat_response)
            data = json.loads(cleaned_output)

            # print(chat_response)
            return data
        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail=str(e))

    @staticmethod
    async def create_assignment(topics: str) -> dict:
        try:
            messages = (
                f"You are a roadmap generator agent. Your task is to analyze the given day's topics: {topics}. "
                f"Based on the topics, generate a single written assignment question. "
                f"Ensure the question is purely text-based and doesn't request the user to include any images. "
                f"Return the output in JSON format like this: "
                f'{{"assignment_question": "Your question here"}}'
            )
            
            chat_response = chat(messages)
            cleaned_output = TaskService.clean_json_output(chat_response)
            data = json.loads(cleaned_output)

            return data
        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail=str(e))

    @staticmethod
    async def create_quiz(topics: str) -> dict:
        try:
            messages = (
                f"You are a roadmap generator agent. Your task is to analyze the given day's topics: {topics}. "
                f"Based on the topics, generate a quiz with exactly 10 questions. Return the output in a valid JSON array format like this: "
                '[{"id": 1, "question": "Your question here", "options": {"a": "Option A", "b": "Option B", "c": "Option C", "d": "Option D"}, "answer": "a"}]'
            )

            chat_response = chat(messages)
            cleaned_output = TaskService.clean_json_output(chat_response)
            data = json.loads(cleaned_output)

            return data
        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail=str(e))

    async def get_days(current_user: dict, task_id: str) -> dict:
        try:

            is_day_exists = await DayModel.find({
                "belongs_to": PydanticObjectId(task_id),
                "user": PydanticObjectId(current_user.id)
            }).to_list()

            if (not is_day_exists):
                raise HTTPException(
                    status_code=404,
                    detail=f"Invalid day id"
                )
            data = [json.loads(task.model_dump_json())
                    for task in is_day_exists]
            return {"message": "Days fetched successfully", "data": data}

        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail="Internal Server Error")

    async def get_day(current_user: dict, task_id: str, day_id: str) -> dict:
        try:

            is_day_exists = await DayModel.find_one({
                "_id": PydanticObjectId(day_id),
                "belongs_to": PydanticObjectId(task_id),
                "user": PydanticObjectId(current_user.id)
            })

            if (not is_day_exists):
                raise HTTPException(
                    status_code=404,
                    detail=f"Invalid day id"
                )

            data = json.loads(is_day_exists.model_dump_json())
            return {"message": "Day fetched successfully", "data": data}

        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail="Internal Server Error")
