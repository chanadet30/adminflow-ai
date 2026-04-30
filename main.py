from fastapi import FastAPI, UploadFile, File
from openai import OpenAI
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import pytesseract
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
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# =========================
# 🧠 CATÉGORISATION MÉTIER
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

    if any(x in f for x in ["loyer", "rent", "immobilier"]):
        return "loyer"

    if any(x in f for x in ["banque", "caisse", "credit", "bnp", "societe generale"]):
        return "finance"

    if any(x in f for x in ["consult", "service", "solution"]):
        return "service"

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

    prompt = f"""
Tu es un assistant administratif professionnel.

Analyse cet email et retourne :
- catégorie
- résumé (1 phrase)
- réponse professionnelle

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
# 📄 FACTURE
# =========================
@app.post("/invoice")
async def analyze_invoice(file: UploadFile = File(...)):
    db = SessionLocal()

    try:
        file_location = f"temp_{file.filename}"

        with open(file_location, "wb") as f:
            f.write(await file.read())

        # OCR
        text = pytesseract.image_to_string(Image.open(file_location))

        # IA extraction simple
        prompt = f"""
Analyse cette facture et retourne STRICTEMENT un JSON :

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

        # Nettoyage JSON
        cleaned = raw.replace("```json", "").replace("```", "").strip()

        try:
            parsed = json.loads(cleaned)
        except:
            parsed = {
                "error": "Parsing échoué",
                "raw": cleaned
            }

        # 💰 NORMALISATION MONTANT
        try:
            montant = parsed.get("montant", "0")
            montant = montant.replace("€", "").replace(",", ".").strip()
            parsed["montant"] = str(float(montant))
        except:
            parsed["montant"] = "0"

        # 🏷️ CATÉGORIE AUTOMATIQUE
        fournisseur = parsed.get("fournisseur", "")
        parsed["categorie"] = detect_category(fournisseur)

        # 💾 DB
        db.add(Analysis(type="facture", content=json.dumps(parsed)))
        db.commit()

        return {"invoice_data": parsed}

    except Exception as e:
        return {"error": str(e)}


# =========================
# 📊 HISTORIQUE
# =========================
@app.get("/history")
def get_history():
    db = SessionLocal()
    data = db.query(Analysis).all()

    return [
        {"type": item.type, "content": item.content}
        for item in data
    ]


# =========================
# 📈 STATS SIMPLES
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
                montant = float(parsed.get("montant", "0"))
                total += montant
                count += 1
            except:
                continue

    return {
        "total_depenses": total,
        "nombre_factures": count
    }


# =========================
# 📊 DASHBOARD AVANCÉ
# =========================
@app.get("/advanced-stats")
def advanced_stats():
    db = SessionLocal()
    data = db.query(Analysis).all()

    categories = {}
    monthly = {}

    for item in data:
        if item.type == "facture":
            try:
                parsed = json.loads(item.content)

                montant = float(parsed.get("montant", "0"))
                cat = parsed.get("categorie", "autre")
                date = parsed.get("date", "2025-01-01")

                # 📊 catégories
                categories[cat] = categories.get(cat, 0) + montant

                # 📅 mensuel
                month = date[:7]
                monthly[month] = monthly.get(month, 0) + montant

            except:
                continue

    return {
        "categories": categories,
        "monthly": monthly
    }