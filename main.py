# main.py

import os
import stripe
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# USER FAKE (simplifié pour ton setup actuel)
def get_user(db: Session):
    return db.query(models.User).first()

# =========================
# 📧 ANALYSE EMAIL
# =========================
@app.post("/email")
def analyze_email(data: dict, db: Session = Depends(get_db)):
    user = get_user(db)

    content = data.get("content")

    result = f"Analyse IA simulée :\n\n{content[:200]}..."

    # 🔥 SAUVEGARDE HISTORIQUE
    history = models.History(
        user_id=user.id,
        content=content,
        result=result
    )
    db.add(history)

    # incrément usage
    user.usage = (user.usage or 0) + 1

    db.commit()

    return {"result": result}


# =========================
# 📜 HISTORIQUE
# =========================
@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    user = get_user(db)

    history = (
        db.query(models.History)
        .filter(models.History.user_id == user.id)
        .order_by(models.History.id.desc())
        .limit(10)
        .all()
    )

    return [
        {
            "content": h.content,
            "result": h.result
        }
        for h in history
    ]


# =========================
# 👤 USER INFO
# =========================
@app.get("/me")
def me(db: Session = Depends(get_db)):
    user = get_user(db)

    return {
        "email": user.email,
        "premium": user.premium,
        "usage": user.usage,
    }


# =========================
# 💳 STRIPE
# =========================
@app.post("/create-checkout-session")
def create_checkout_session():
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="subscription",
        line_items=[
            {
                "price_data": {
                    "currency": "eur",
                    "product_data": {
                        "name": "AdminFlow Premium",
                    },
                    "unit_amount": 900,
                    "recurring": {"interval": "month"},
                },
                "quantity": 1,
            }
        ],
        success_url="http://localhost:3000/dashboard",
        cancel_url="http://localhost:3000/dashboard",
    )

    return {"url": session.url}


@app.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    event = stripe.Webhook.construct_event(
        payload, sig_header, WEBHOOK_SECRET
    )

    if event["type"] == "checkout.session.completed":
        user = get_user(db)
        user.premium = True
        db.commit()

    return {"status": "ok"}