from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from PyPDF2 import PdfReader

app = FastAPI()

# =========================
# 🌐 CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 🔑 OpenAI
# =========================
client = OpenAI()

# =========================
# TEST
# =========================
@app.get("/test")
def test():
    return {"msg": "API OK 🚀"}

# =========================
# ROOT
# =========================
@app.get("/")
def root():
    return {"status": "AdminFlow AI OK 🚀"}

# =========================
# 📧 MODEL
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

        return {"result": response.output_text}

    except Exception as e:
        return {"error": str(e)}

# =========================
# 📄 INVOICE ANALYSIS (PDF)
# =========================
@app.post("/invoice")
async def analyze_invoice(file: UploadFile = File(...)):
    try:
        # lire le fichier PDF
        reader = PdfReader(file.file)
        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        if not text:
            text = "Impossible d'extraire le texte du PDF"

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=f"""
Analyse cette facture :

{text}

Donne :
- fournisseur
- montant
- date
- résumé
"""
        )

        return {"result": response.output_text}

    except Exception as e:
        return {"error": str(e)}