from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import stripe
import os
from openai import OpenAI

from database import SessionLocal, engine, Base
import models

# -------------------------
# INIT
# -------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------
# CONFIG
# -------------------------
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

PRICE_ID = "price_1TTM341e5DKL1tszQvMtQJ7C"
CURRENT_USER_EMAIL = "chanadet30@gmail.com"

print("🔥 BACKEND VERSION V2 ACTIVE")

# -------------------------
# ROUTES
# -------------------------

@app.get("/me")
def get_me(db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.email == CURRENT_USER_EMAIL
    ).first()

    if not user:
        return {"email": CURRENT_USER_EMAIL, "premium": False}

    return {"email": user.email, "premium": user.premium}


@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    emails = db.query(models.Email).filter(
        models.Email.user_email == CURRENT_USER_EMAIL
    ).order_by(models.Email.id.desc()).all()

    return [{"content": e.content, "result": e.result} for e in emails]


# -------------------------
# ANALYSE IA
# -------------------------
@app.post("/email")
async def analyze_email(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    content = body.get("content")

    print("📨 EMAIL REÇU:", content)

    if not content:
        return {"result": "Aucun contenu"}

    # 🔒 LIMIT FREE
    user = db.query(models.User).filter(
        models.User.email == CURRENT_USER_EMAIL
    ).first()

    if not user:
        user = models.User(email=CURRENT_USER_EMAIL, premium=False)
        db.add(user)
        db.commit()

    if not user.premium:
        count = db.query(models.Email).filter(
            models.Email.user_email == CURRENT_USER_EMAIL
        ).count()

        if count >= 3:
            return {"error": "LIMIT_REACHED"}

    # -------------------------
    # TEST OPENAI
    # -------------------------
    try:
        print("🚀 OPENAI CALL START")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Assistant professionnel qui analyse les emails."
                },
                {
                    "role": "user",
                    "content": f"""
Analyse cet email et réponds EXACTEMENT avec :

📌 Résumé :
(1 phrase)

🎯 Intention :
(type)

✉️ Réponse suggérée :
(réponse pro)

EMAIL :
{content}
"""
                }
            ]
        )

        result = response.choices[0].message.content

        print("✅ OPENAI OK")

    except Exception as e:
        print("❌ ERREUR OPENAI:", e)
        result = "Erreur IA"

    # SAVE
    new_email = models.Email(
        user_email=CURRENT_USER_EMAIL,
        content=content,
        result=result
    )

    db.add(new_email)
    db.commit()

    return {"result": result}


# -------------------------
# STRIPE
# -------------------------
@app.post("/create-checkout-session")
def create_checkout():
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{
            "price": PRICE_ID,
            "quantity": 1,
        }],
        success_url="http://localhost:3000/dashboard",
        cancel_url="http://localhost:3000/dashboard",
        customer_email=CURRENT_USER_EMAIL
    )

    return {"url": session.url}


# -------------------------
# WEBHOOK
# -------------------------
@app.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except Exception as e:
        print("❌ Webhook error:", e)
        return {"status": "error"}

    print("📩 EVENT:", event["type"])

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        email = None

        if session.customer_details:
            email = session.customer_details.email

        if not email and session.customer:
            customer = stripe.Customer.retrieve(session.customer)
            email = customer.email

        print("📧 EMAIL:", email)

        if not email:
            return {"status": "error"}

        user = db.query(models.User).filter(
            models.User.email == email
        ).first()

        if not user:
            user = models.User(email=email, premium=True)
            db.add(user)
        else:
            user.premium = True

        db.commit()

        print("🔥 PREMIUM ACTIVÉ")

    return {"status": "success"}