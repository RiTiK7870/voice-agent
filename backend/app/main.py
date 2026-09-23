from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, health
from app.websocket import audiohook

app = FastAPI(
    title="Enterprise AI Voice Agent POC",
    version="1.0.0",
    description="Genesys AudioHook -> STT -> LangGraph/RAG -> LLM -> TTS architecture"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "X-Session-ID",
        "X-Transcript",
        "X-Answer",
        "X-Escalated",
        "X-Sources",
    ],
)

app.include_router(health.router, tags=["health"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(audiohook.router, prefix="/ws", tags=["audio"])


@app.get("/")
def root():
    return {
        "name": "Enterprise AI Voice Agent POC",
        "status": "running",
        "architecture": "Genesys AudioHook -> STT -> LangGraph/RAG -> LLM -> TTS"
    }