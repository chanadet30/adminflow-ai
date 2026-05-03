from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
import stripe
import base64

from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta

from sqlalchemy import create_engine, Column, String, Boolean, Integer
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# =========================
# CONFIG
# =========================
load_dotenv()

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
FREE_LIMIT = 5

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# =========================
# DB
# =========================
DATABASE_URL = "sqlite:///./adminflow.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    email = Column(String, primary_key=True, index=True)
    password = Column(String)
    usage = Column(Integer, default=0)
    premium = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# AUTH
# =========================
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
security = HTTPBearer()

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(hours=24)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")

# =========================
# APP
# =========================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ en prod limiter
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# MODELS
# =========================
class EmailRequest(BaseModel):
    content: str

class AuthRequest(BaseModel):
    email: str
    password: str

# =========================
# AUTH ROUTES
# =========================
@app.post("/signup")
def signup(data: AuthRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "User exists")

    user = User(
        email=data.email,
        password=hash_password(data.password)
    )

    db.add(user)
    db.commit()

    return {"message": "Account created"}

@app.post("/login")
def login(data: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(401, "Invalid credentials")

    token = create_access_token({"sub": user.email})
    return {"access_token": token}

# =========================
# USER
# =========================
@app.get("/me")
def get_me(user_email: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_email).first()

    return {
        "email": user.email,
        "usage": user.usage,
        "premium": user.premium
    }

# =========================
# DEBUG PREMIUM
# =========================
@app.get("/force-premium")
def force_premium(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {"error": "user not found"}

    user.premium = True
    db.commit()

    return {"status": "premium activé"}

# =========================
# EMAIL IA
# =========================
@app.post("/email")
def analyze_email(request: EmailRequest, user_email: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_email).first()

    if not user:
        raise HTTPException(404)

    if not user.premium and user.usage >= FREE_LIMIT:
        raise HTTPException(403, "Limit reached")

    user.usage += 1
    db.commit()

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=f"""
Analyse cet email :

- Catégorie
- Résumé
- Réponse professionnelle

Email :
{request.content}
"""
    )

    return {
        "result": response.output_text,
        "usage": user.usage,
        "premium": user.premium
    }

# =========================
# FACTURE IA
# =========================
@app.post("/invoice")
async def analyze_invoice(
    file: UploadFile = File(...),
    user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == user_email).first()

    if not user:
        raise HTTPException(404)

    if not user.premium:
        raise HTTPException(403, "Premium required")

    content = await file.read()
    base64_file = base64.b64encode(content).decode("utf-8")

    response = client.responses.create(
        model="gpt-4.1",
        input=[{
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "Analyse cette facture et donne montant, TVA, date, fournisseur"
                },
                {
                    "type": "input_image",
                    "image_base64": base64_file
                }
            ]
        }]
    )

    user.usage += 1
    db.commit()

    return {"result": response.output_text}

# =========================
# STRIPE CHECKOUT
# =========================
@app.post("/create-checkout-session")
def create_checkout(user_email: str = Depends(get_current_user)):
    customer = stripe.Customer.create(email=user_email)

    session = stripe.checkout.Session.create(
        customer=customer.id,
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {"name": "AdminFlow Premium"},
                "unit_amount": 900,
                "recurring": {"interval": "month"},
            },
            "quantity": 1,
        }],
        success_url="http://localhost:3000",
        cancel_url="http://localhost:3000",
    )

    return {"url": session.url}

# =========================
# STRIPE WEBHOOK
# =========================
@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            STRIPE_WEBHOOK_SECRET
        )
    except Exception:
        raise HTTPException(400, "Webhook error")

    if event["type"] == "invoice.paid":
        customer_id = event["data"]["object"]["customer"]

        customer = stripe.Customer.retrieve(customer_id)
        email = customer.get("email")

        db = SessionLocal()
        user = db.query(User).filter(User.email == email).first()

        if user:
            user.premium = True
            db.commit()

    return {"status": "ok"}