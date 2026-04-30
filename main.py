from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# =========================
# DEBUG
# =========================
API_KEY = os.getenv("OPENAI_API_KEY")

print("API KEY:", API_KEY)


# =========================
# ROOT
# =========================
@app.get("/")
def root():
    return {
        "status": "OK 🚀",
        "api_key_loaded": API_KEY is not None
    }


# =========================
# MODEL
# =========================
class EmailRequest(BaseModel):
    content: str


# =========================
# EMAIL (test simple)
# =========================
@app.post("/email")
def analyze_email(request: EmailRequest):

    # TEST sans OpenAI
    return {
        "message": "API fonctionne",
        "content": request.content,
        "api_key_loaded": API_KEY is not None
    }