from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import stripe
import os

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
# STRIPE
# -------------------------
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

PRICE_ID = "price_1TTM341e5DKL1tszQvMtQJ7C"

print("🔐 STRIPE KEY:", stripe.api_key)
print("🔐 WEBHOOK SECRET:", WEBHOOK_SECRET)

CURRENT_USER_EMAIL = "chanadet30@gmail.com"

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


@app.post("/email")
async def analyze_email(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    content = body.get("content")

    if not content:
        return {"result": "Aucun contenu"}

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

    result = f"Analyse IA:\n{content[:300]}..."

    new_email = models.Email(
        user_email=CURRENT_USER_EMAIL,
        content=content,
        result=result
    )

    db.add(new_email)
    db.commit()

    return {"result": result}


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
# WEBHOOK FIX FINAL
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
        print("❌ Webhook signature error:", e)
        return {"status": "error"}

    print("📩 EVENT:", event["type"])

    try:
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]

            email = None

            # 🔥 FIX principal
            if hasattr(session, "customer_details") and session.customer_details:
                email = session.customer_details.email

            # 🔥 fallback
            if not email and hasattr(session, "customer") and session.customer:
                customer = stripe.Customer.retrieve(session.customer)
                email = customer.email

            print("📧 EMAIL:", email)

            if not email:
                print("❌ Aucun email trouvé")
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

    except Exception as e:
        print("❌ WEBHOOK PROCESS ERROR:", e)
        return {"status": "error"}

    return {"status": "success"}