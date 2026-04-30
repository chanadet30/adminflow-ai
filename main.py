from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# =========================
# ROOT
# =========================
@app.get("/")
def root():
    return {"status": "AdminFlow AI OK 🚀"}


# =========================
# MODEL
# =========================
class EmailRequest(BaseModel):
    content: str


# =========================
# EMAIL
# =========================
@app.post("/email")
def analyze_email(request: EmailRequest):
    try:
        # 👉 IMPORTANT : pas de api_key=...
        client = OpenAI()

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=f"""
Tu es un assistant administratif.

Analyse cet email et donne :
- catégorie
- résumé
- réponse pro

Email :
{request.content}
"""
        )

        return {"result": response.output_text}

    except Exception as e:
        return {"error": str(e)}