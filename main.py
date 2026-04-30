from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Charger .env
load_dotenv()

app = FastAPI()

# =========================
# 🔑 DEBUG API KEY
# =========================
API_KEY = os.getenv("OPENAI_API_KEY")

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
# 📧 EMAIL (NOUVELLE API OPENAI)
# =========================
@app.post("/email")
def analyze_email(request: EmailRequest):
    try:
        from openai import OpenAI

        client = OpenAI(api_key=API_KEY)

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

        # récupération du texte
        result = response.output[0].content[0].text

        return {"result": result}

    except Exception as e:
        return {"error": str(e)}