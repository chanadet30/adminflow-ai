from fastapi import FastAPI
from pydantic import BaseModel
import os

app = FastAPI()

class EmailRequest(BaseModel):
    content: str

@app.post("/email")
def analyze_email(request: EmailRequest):
    return {
        "key_used": os.getenv("OPENAI_API_KEY")
    }