from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from models.user import User
from routers.UserRouter import router as user_router
from config import settings

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

@app.get("/", tags = "Home")
def home():
    return "Sintiendo"
app.include_router(user_router)
