from fastapi import HTTPException
import traceback
from core.chat_gpt import chat
from beanie import PydanticObjectId
from models.day import DayModel
from services.task_service import TaskService
import json
from models.videos import VideoModel
from models.articles import ArticleModel
from models.assignments import AssignmentModel
from models.quizzes import QuizModel
import yt_dlp
from googlesearch import search


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

            day_description_and_tasks = await DayNTaskSerivce.create_task_description(is_day_exists.topics, is_day_exists.keyword)
            video_content = DayNTaskSerivce.search_videos_from_topics(
                day_description_and_tasks["topics"], is_day_exists.keyword)
            article_content = await DayNTaskSerivce.list_articles(day_description_and_tasks["topics"], is_day_exists.keyword)
            assignment_content = await DayNTaskSerivce.create_assignment(str(day_description_and_tasks["topics"]), is_day_exists.keyword)
            quiz_content = await DayNTaskSerivce.create_quiz(str(day_description_and_tasks["topics"]), is_day_exists.keyword)

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
    async def create_task_description(topics: str, keyword: str) -> dict:
        try:
            messages = (
                f"You are a roadmap generator agent. Your task is to analyze the given day's topics: {topics}. keyword: {keyword}"
                f"Based on the topics, generate a short and precise description of the day and list only the relevant subtopics covered. "
                f"Do not include any unnecessary or irrelevant topics. strictly Return the output in valid JSON format like this: "
                '{"description": "", "topics": []}'
            )

            chat_response = chat(messages)
            print("response ", chat_response)
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
    async def create_article_list(topics: str) -> dict:
        try:
            messages = (
                f"You are a roadmap generator agent. Your task is to analyze the given day's topics: {topics}. "
                f"Based on the topics, generate a list of the best learning articles from reliable sources. "
                f"Ensure no duplicate articles for the same topic. "
                f"Return the output strictly in pure JSON format, like this: "
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
    def search_videos_from_topics(topics, keyword):
        ydl_opts = {
            "quiet": True,
            "extract_flat": True,
            "force_generic_extractor": True,
        }

        results = []

        for topic in topics:
            # Search for the top 1 video
            search_url = f"ytsearch1:{topic} in ({keyword})"

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(search_url, download=False)

            if 'entries' in info and info['entries']:
                entry = info['entries'][0]
                results.append({
                    "topic": topic,
                    "link": entry['url']
                })

        return results

    @staticmethod
    async def list_articles(topics, keyword):
        unique_links = set()
        results = []

        print("hello 2")

        for topic in topics:
            query = topic + " in " + keyword
            try:
                found = False
                # Set num_results to 1 per topic
                for result in search(query, num_results=1):
                    if result not in unique_links:
                        unique_links.add(result)
                        results.append({"topic": topic, "link": result})
                        found = True
                        break  # Only take the first valid link

                if not found:
                    print(
                        f"No articles found for topic '{topic}'. Skipping...")
            except:
                print(f"Skipping topic '{topic}' due to an unexpected issue.")

        return results

    @staticmethod
    async def create_assignment(topics: str, keyword) -> dict:
        try:
            messages = (
                f"You are a roadmap generator agent. Your task is to analyze the given day's topics: {topics}. keyword: {keyword}"
                f"Based on the topics, generate a single written assignment question. "
                f"Ensure the question is purely text-based and doesn't request the user to include any images. "
                f"strictly Return the output in JSON format like this: "
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
    async def create_quiz(topics: str, keyword: str) -> dict:
        try:
            messages = (
                f"You are a roadmap generator agent. Your task is to analyze the given day's topics: {topics}. keyword: {keyword}"
                f"strictly Based on the topics, generate a quiz with exactly 10 questions. Return the output in a valid JSON array format like this: "
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

    @staticmethod
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

    @staticmethod
    async def update_day(current_user: dict, task_id: str, day_id: str) -> dict:
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

            await is_day_exists.update({
                "$set": {
                    "status": True
                }
            })

            return {"message": "Day updated successfully", "data": data}

        except Exception as e:
            # Logs the full error traceback
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail="Internal Server Error")
