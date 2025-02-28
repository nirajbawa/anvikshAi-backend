from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dependencies.database import init_db
from api.v1.routes.user_auth import user_auth
from api.v1.routes.tasks import task
from api.v1.routes.content import content
from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    await init_db()
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
    return {"Hello": "World"}


app.include_router(user_auth, prefix="/auth", tags=["Authentication"])
app.include_router(task, prefix="/task", tags=["Tasks"])
app.include_router(content, prefix="/content", tags=["Content"])

# uvicorn app.main:app --reload
# fastapi dev app/main.py
