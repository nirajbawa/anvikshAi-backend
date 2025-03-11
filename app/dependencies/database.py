from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.user import UserModel
from app.models.tasks import TaskModel
from app.models.day import DayModel
from app.models.videos import VideoModel
from app.models.articles import ArticleModel
from app.models.assignments import AssignmentModel
from app.models.quizzes import QuizModel
from app.models.certificates import CertificateModel
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("DATABASE_URI")


async def init_db():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client.fastapi_db  # Database name
    await init_beanie(database=db, document_models=[UserModel, TaskModel, DayModel, VideoModel, ArticleModel, AssignmentModel, QuizModel, CertificateModel])
