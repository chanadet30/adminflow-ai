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

# CORS (autorise Railway + localhost)
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

    if any(x in f for x in ["banque", "credit", "bnp", "societe generale"]):
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
    client = get_client()

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
    client = get_client()

    try:
        file_location = f"temp_{file.filename}"

        with open(file_location, "wb") as f:
            f.write(await file.read())

        # OCR
        text = pytesseract.image_to_string(Image.open(file_location))

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
        cleaned = raw.replace("```json", "").replace("```", "").strip()

        try:
            parsed = json.loads(cleaned)
        except:
            parsed = {"error": "Parsing échoué", "raw": cleaned}

        # 💰 montant
        try:
            montant = parsed.get("montant", "0")
            montant = montant.replace("€", "").replace(",", ".").strip()
            parsed["montant"] = str(float(montant))
        except:
            parsed["montant"] = "0"

        # 🏷️ catégorie
        fournisseur = parsed.get("fournisseur", "")
        parsed["categorie"] = detect_category(fournisseur)

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

    return [{"type": i.type, "content": i.content} for i in data]


# =========================
# 📈 STATS
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