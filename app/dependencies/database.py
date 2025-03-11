from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from models.user import UserModel
from models.tasks import TaskModel
from models.day import DayModel
from models.videos import VideoModel
from models.articles import ArticleModel
from models.assignments import AssignmentModel
from models.quizzes import QuizModel
from models.certificates import CertificateModel
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("DATABASE_URI")


async def init_db():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client.fastapi_db  # Database name
    await init_beanie(database=db, document_models=[UserModel, TaskModel, DayModel, VideoModel, ArticleModel, AssignmentModel, QuizModel, CertificateModel])
