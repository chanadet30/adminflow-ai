from fastapi import FastAPI, UploadFile, File
from openai import OpenAI
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import json

# DB
from database import SessionLocal, engine
from models import Base, Analysis

# Création DB
Base.metadata.create_all(bind=engine)

# Charger variables env
load_dotenv()

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 🔐 OPENAI SAFE INIT
# =========================
def get_client():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise Exception("OPENAI_API_KEY manquante")

    return OpenAI(api_key=api_key)


# =========================
# 🧠 CATÉGORISATION
# =========================
def detect_category(fournisseur):
    f = fournisseur.lower()

    if any(x in f for x in ["edf", "engie", "energie"]):
        return "energie"
    if any(x in f for x in ["orange", "sfr", "bouygues", "free"]):
        return "telecom"
    if any(x in f for x in ["sncf", "uber", "ratp", "taxi"]):
        return "transport"
    if any(x in f for x in ["netflix", "spotify", "amazon"]):
        return "abonnement"
    if any(x in f for x in ["loyer", "rent"]):
        return "loyer"
    if any(x in f for x in ["banque", "credit", "bnp"]):
        return "finance"

    return "autre"


# =========================
# ROOT
# =========================
@app.get("/")
def root():
    return {"status": "AdminFlow AI OK 🚀"}


# =========================
# 📧 EMAIL
# =========================
@app.post("/email")
def analyze_email(content: str):
    db = SessionLocal()
    client = get_client()

    prompt = f"""
Analyse cet email et retourne :
- catégorie
- résumé
- réponse pro

Email :
{content}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.choices[0].message.content

    db.add(Analysis(type="email", content=result))
    db.commit()

    return {"result": result}


# =========================
# 📄 FACTURE (SANS OCR)
# =========================
@app.post("/invoice")
async def analyze_invoice(file: UploadFile = File(...)):
    db = SessionLocal()
    client = get_client()

    try:
        file_location = f"temp_{file.filename}"

        with open(file_location, "wb") as f:
            f.write(await file.read())

        # 👉 Pas de Tesseract (Railway incompatible)
        text = "Facture image reçue"

        prompt = f"""
Analyse cette facture et retourne JSON :

{{
  "fournisseur": "...",
  "montant": "...",
  "date": "YYYY-MM-DD"
}}

Texte :
{text}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        raw = response.choices[0].message.content
        cleaned = raw.replace("```json", "").replace("```", "").strip()

        try:
            parsed = json.loads(cleaned)
        except:
            parsed = {"error": "Parsing échoué", "raw": cleaned}

        # montant
        try:
            montant = parsed.get("montant", "0")
            montant = montant.replace("€", "").replace(",", ".")
            parsed["montant"] = str(float(montant))
        except:
            parsed["montant"] = "0"

        # catégorie
        parsed["categorie"] = detect_category(parsed.get("fournisseur", ""))

        db.add(Analysis(type="facture", content=json.dumps(parsed)))
        db.commit()

        return {"invoice_data": parsed}

    except Exception as e:
        return {"error": str(e)}


# =========================
# 📊 STATS
# =========================
@app.get("/stats")
def get_stats():
    db = SessionLocal()
    data = db.query(Analysis).all()

    total = 0
    count = 0

    for item in data:
        if item.type == "facture":
            try:
                parsed = json.loads(item.content)
                total += float(parsed.get("montant", "0"))
                count += 1
            except:
                pass

    return {
        "total_depenses": total,
        "nombre_factures": count
    }