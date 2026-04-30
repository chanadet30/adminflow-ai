from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

# 🔥 CORS (CORRECTION ICI)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 👈 IMPORTANT (pas "*")
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI()

class EmailRequest(BaseModel):
    content: str

@app.get("/")
def root():
    return {"status": "OK"}

@app.post("/email")
def analyze_email(request: EmailRequest):
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=request.content
        )
        return {"result": response.output_text}
    except Exception as e:
        return {"error": str(e)}