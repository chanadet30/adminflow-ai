import os
import stripe
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI()

# CORS (important pour frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ENV VARIABLES
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

print("🔐 STRIPE KEY:", STRIPE_SECRET_KEY)
print("🔐 WEBHOOK SECRET:", STRIPE_WEBHOOK_SECRET)

stripe.api_key = STRIPE_SECRET_KEY

# FAKE DB (temporaire)
users = {}

SECRET_KEY = "secret"
ALGORITHM = "HS256"

security = HTTPBearer()

# =====================
# AUTH
# =====================

class User(BaseModel):
    email: str
    password: str

def create_token(email):
    return jwt.encode({"email": email}, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["email"]
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

# =====================
# ROUTES
# =====================

@app.post("/login")
def login(user: User):
    users[user.email] = {
        "premium": False,
        "email": user.email
    }
    return {"access_token": create_token(user.email)}

@app.get("/me")
def me(email: str = Depends(get_current_user)):
    return users.get(email, {"email": email, "premium": False})

# =====================
# STRIPE CHECKOUT
# =====================

@app.post("/create-checkout-session")
def create_checkout(email: str = Depends(get_current_user)):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        customer_email=email,
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {
                    "name": "AdminFlow Premium"
                },
                "unit_amount": 1000,
            },
            "quantity": 1,
        }],
        success_url="http://localhost:3000",
        cancel_url="http://localhost:3000",
    )

    return {"url": session.url}

# =====================
# WEBHOOK STRIPE
# =====================

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
        raise HTTPException(status_code=400, detail="Webhook error")

    print("📩 EVENT:", event["type"])

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        email = session.get("customer_email")

        print("📧 EMAIL:", email)

        if email in users:
            users[email]["premium"] = True
            print("🔥 PREMIUM ACTIVÉ")

    return {"status": "ok"}