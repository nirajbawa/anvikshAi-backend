from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from api.v1.routes.user_auth import user_auth
from fastapi.middleware.cors import CORSMiddleware 
from dependencies.database import init_db
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    await init_db() 
    yield  # Allows the app to run
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)

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

app.include_router(user_auth, prefix="/auth", tags=["User Authentication"])

# uvicorn app.main:app --reload
# fastapi dev app/main.py
