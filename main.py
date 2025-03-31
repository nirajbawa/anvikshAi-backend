from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.dependencies.database import init_db
from app.dependencies.admin_config import admin_init
from app.api.v1.routes.user_auth import user_auth
from app.api.v1.routes.tasks import task
from app.api.v1.routes.content import content
from app.api.v1.routes.payment import payment
from app.api.v1.routes.admin_auth import admin_auth
from app.api.v1.routes.admin_users import admin_users
from app.api.v1.routes.admin_expert import admin_expert
from app.api.v1.routes.expert_auth import expert_auth
from app.api.v1.routes.expert_courses import expert_courses
from app.api.v1.routes.admin_courses import admin_courses
from app.api.v1.routes.admin_mentor import admin_mentor
from app.api.v1.routes.mentor_auth import mentor_auth
from app.api.v1.routes.user_mentor import user_mentor
from app.api.v1.routes.mentor import mentor
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.openapi.utils import get_openapi
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    await init_db()
    await admin_init()
    yield  # Allows the app to run
    print("Shutting down...")


app = FastAPI(lifespan=lifespan,
              title="AnvikshAI API",
              description="",
              docs_url="/docs",
              openapi_tags=[{"name": "Authentication", "description": "Login & User management (treated email as username)"}])

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello World"}


app.include_router(user_auth, prefix="/auth", tags=["Authentication"])
app.include_router(task, prefix="/task", tags=["Tasks"])
app.include_router(content, prefix="/content", tags=["Content"])
app.include_router(payment, prefix="/payment", tags=["Payment"])
app.include_router(user_mentor, prefix="/mentor",
                   tags=["Mentor"])
app.include_router(admin_auth, prefix="/admin", tags=["Admin"])
app.include_router(admin_users, prefix="/admin/users", tags=["Admin Users"])
app.include_router(admin_expert, prefix="/admin/expert",
                   tags=["Admin Expert"])
app.include_router(admin_mentor, prefix="/admin/mentor",
                   tags=["Admin Mentor"])
app.include_router(admin_courses, prefix="/admin/courses",
                   tags=["Admin Courses"])
app.include_router(expert_auth, prefix="/expert/auth",
                   tags=["Expert Auth"])
app.include_router(expert_courses, prefix="/expert/courses",
                   tags=["Expert Courses"])
app.include_router(mentor_auth, prefix="/mentor/auth",
                   tags=["Mentor Auth"])
app.include_router(mentor, prefix="/mentor/dashboard",
                   tags=["Mentor dashboard"])

