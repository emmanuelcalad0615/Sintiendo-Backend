from fastapi import FastAPI

app = FastAPI()

app.title = "Sintiendo"

@app.get("/", tags = "Home")
def home():
    return "EmoKids"
