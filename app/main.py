from fastapi import FastAPI
from app.api.v1.endpoints import chatbot
from app.core.config import settings

app = FastAPI(
    title="Cybersecurity Chatbot API",
    description="An AI chatbot specializing in cybersecurity, powered by Ollama and a SQL agent.",
    version="1.0.0",
)

app.include_router(chatbot.router, prefix="/api/v1", tags=["chatbot"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Cybersecurity Chatbot API"}