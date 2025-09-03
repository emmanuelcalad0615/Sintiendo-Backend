from fastapi import FastAPI
from database import engine, Base
from models.user import User
from routers.UserRouter import router as user_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.title = "Sintiendo"

@app.get("/", tags = "Home")
def home():
    return "Sintiendo"
app.include_router(user_router)
