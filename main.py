from fastapi import FastAPI

app = FastAPI()

app.title = "Emokids"

@app.get("/", tags = "Home")
def home():
    return "EmoKids"