from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# =========================
# 🔑 OpenAI
# =========================
API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY) if API_KEY else None

print("API KEY LOADED:", API_KEY is not None)


# =========================
# ROOT
# =========================
@app.get("/")
def root():
    return {
        "status": "AdminFlow AI OK 🚀",
        "api_key_loaded": API_KEY is not None
    }


# =========================
# 📧 MODELE
# =========================
class EmailRequest(BaseModel):
    content: str


# =========================
# 📧 EMAIL
# =========================
@app.post("/email")
def analyze_email(request: EmailRequest):
    try:
        if not client:
            return {"error": "OpenAI API key missing"}

        prompt = f"""
Tu es un assistant administratif professionnel.

Analyse cet email et donne :
- catégorie
- résumé
- réponse pro

Email :
{request.content}
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # 👈 modèle stable
            messages=[{"role": "user", "content": prompt}]
        )

        result = response.choices[0].message.content

        return {"result": result}

    except Exception as e:
        return {"error": str(e)}