import os
import stripe
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy import create_engine, Column, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base

# =========================
# CONFIG
# =========================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ENV
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

print("🔐 STRIPE KEY:", STRIPE_SECRET_KEY)
print("🔐 WEBHOOK SECRET:", STRIPE_WEBHOOK_SECRET)

stripe.api_key = STRIPE_SECRET_KEY

SECRET_KEY = "secret"
ALGORITHM = "HS256"

security = HTTPBearer()

# =========================
# DATABASE
# =========================
DATABASE_URL = "sqlite:///./adminflow.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    email = Column(String, primary_key=True, index=True)
    password = Column(String)
    premium = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

# =========================
# AUTH
# =========================
class AuthRequest(BaseModel):
    email: str
    password: str

def create_token(email):
    return jwt.encode({"sub": email}, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

# =========================
# AUTH ROUTES
# =========================
@app.post("/login")
def login(data: AuthRequest):
    db = SessionLocal()

    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        user = User(email=data.email, password=data.password)
        db.add(user)
        db.commit()

    token = create_token(data.email)

    return {"access_token": token}

@app.get("/me")
def me(user_email: str = Depends(get_current_user)):
    db = SessionLocal()
    user = db.query(User).filter(User.email == user_email).first()

    return {
        "email": user.email,
        "premium": user.premium
    }

# =========================
# STRIPE CHECKOUT
# =========================
@app.post("/create-checkout-session")
def create_checkout(user_email: str = Depends(get_current_user)):

    customer = stripe.Customer.create(
        email=user_email
    )

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
# WEBHOOK STRIPE (FIX FINAL)
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
    except Exception as e:
        print("❌ Webhook error:", e)
        raise HTTPException(status_code=400)

    print("📩 EVENT:", event["type"])

    # 🔥 CHECKOUT COMPLETED
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        customer_id = session.customer
        print("🧾 CUSTOMER:", customer_id)

        if customer_id:
            customer = stripe.Customer.retrieve(customer_id)
            email = customer.email

            print("📧 EMAIL:", email)

            db = SessionLocal()
            user = db.query(User).filter(User.email == email).first()

            if user:
                user.premium = True
                db.commit()
                print("🔥 PREMIUM ACTIVÉ")

    # 🔥 BONUS sécurité : abonnement confirmé
    if event["type"] == "invoice.paid":
        invoice = event["data"]["object"]

        customer_id = invoice.customer

        if customer_id:
            customer = stripe.Customer.retrieve(customer_id)
            email = customer.email

            db = SessionLocal()
            user = db.query(User).filter(User.email == email).first()

            if user:
                user.premium = True
                db.commit()
                print("🔥 PREMIUM ACTIVÉ (invoice)")

    return {"status": "ok"}