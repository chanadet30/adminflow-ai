from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# 🔑 clé
API_KEY = os.getenv("OPENAI_API_KEY")

print("API KEY =", API_KEY)

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
# 📧 MODELE
# =========================
class EmailRequest(BaseModel):
    content: str


# =========================
# 📧 EMAIL (sans OpenAI pour test)
# =========================
@app.post("/email")
def analyze_email(request: EmailRequest):
    return {
        "message": "API fonctionne",
        "content_recu": request.content,
        "api_key_loaded": API_KEY is not None
    }