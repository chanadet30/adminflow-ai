from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = FastAPI()

# =========================
# 🌐 CORS (IMPORTANT FRONTEND)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en prod on limitera
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 🔑 OpenAI
# =========================
client = OpenAI()  # utilise automatiquement OPENAI_API_KEY

# =========================
# ROOT
# =========================
@app.get("/")
def root():
    return {"status": "AdminFlow AI OK 🚀"}

# =========================
# 📧 MODELE
# =========================
class EmailRequest(BaseModel):
    content: str

# =========================
# 📧 EMAIL ANALYSIS
# =========================
@app.post("/email")
def analyze_email(request: EmailRequest):
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=f"""
Tu es un assistant administratif professionnel.

Analyse cet email et retourne :
- catégorie
- résumé (1 phrase)
- réponse professionnelle

Email :
{request.content}
"""
        )

        result = response.output_text

        return {"result": result}

    except Exception as e:
        return {"error": str(e)}