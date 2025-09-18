from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  
from database import engine, Base
from models.user import User
from models.diary import DiaryEntry, EmotionRecord
from models.media import MediaFile  
from routers.UserRouter import router as user_router
from routers.DiaryRouter import router as diary_router
from routers.MediaRouter import router as media_router  
from config import settings
import os


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.title = "Sintiendo"
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_url,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
@app.get("/", tags = "Home")
def home():
    return "Sintiendo"
app.include_router(user_router)

app.include_router(diary_router)  
app.include_router(media_router)