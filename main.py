import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from search import ask

app = FastAPI(title="RAG Chatbot API")

# FRONTEND_URL la irukkura URL mattum allow (comma vachu multiple kudukkalam)
# Local .env = http://localhost:5173, Render env = production UI URL
allowed_origins = [url.strip() for url in os.getenv("FRONTEND_URL", "").split(",") if url.strip()]
if not allowed_origins:
    print("FRONTEND_URL not set - all browser requests blocked")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)

@app.get("/")
def home():
    return {"status": "RAG Chatbot API running"}

# React -> question -> search + Groq -> answer
@app.post("/chat")
def chat(req: ChatRequest):
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question required")
    try:
        answer, rows = ask(question)
    except Exception as err:
        print("Chat error:", err)
        raise HTTPException(status_code=502, detail="AI service not reachable, try again")
    sources = [{"text": content, "score": round(float(score), 2)} for content, score in rows]
    return {"answer": answer, "sources": sources}
