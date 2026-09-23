# Enterprise AI Voice Agent — Full POC Skeleton

## Architecture

Genesys Cloud
    |
    | AudioHook / WebSocket
    v
Python FastAPI backend
    |
    +--> Streaming STT
    |
    +--> LangGraph
            |
            +--> RAG / Knowledge Base
            |
            +--> Approved LLM (Azure OpenAI / OpenAI-compatible)
    |
    +--> TTS
    |
    v
Genesys Cloud
    |
    v
Customer

## Important

This repository intentionally does NOT invent the exact Genesys AudioHook protocol
or TCS-specific STT/TTS configuration. The TCS/Genesys team must provide those
contracts/configuration. The placeholders are clearly marked in the code.

## Run locally without API keys

Windows:

    py -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt

Copy:

    copy .env.example .env

Keep:

    LLM_PROVIDER=mock
    SPEECH_PROVIDER=mock

Run:

    uvicorn app.main:app --reload

Open:

    http://127.0.0.1:8000/docs

Test POST /api/chat:

    {
      "session_id": "demo-1",
      "message": "What is your refund policy?"
    }

Test unknown:

    {
      "session_id": "demo-2",
      "message": "What is the weather on Mars?"
    }

## Enable Azure/OpenAI LLM

Only after the organization gives you approved credentials:

    LLM_PROVIDER=azure_openai

Then populate:

    AZURE_OPENAI_ENDPOINT=
    AZURE_OPENAI_API_KEY=
    AZURE_OPENAI_DEPLOYMENT=

For OpenAI-compatible:

    LLM_PROVIDER=openai

and populate:

    OPENAI_API_KEY=
    OPENAI_MODEL=

## Speech

The speech files are intentionally adapters.

When TCS gives the approved STT/TTS service, implement it in:

    app/speech/stt.py
    app/speech/tts.py

## Genesys

The AudioHook WebSocket entry point is:

    ws://localhost:8000/ws/audiohook

For actual Genesys use, deploy behind HTTPS/WSS and implement the exact
AudioHook lifecycle, authentication, media format, messages and outbound
audio protocol provided by your TCS/Genesys team.

## Production hardening

Before production:
- Use Entra ID / approved authentication.
- Store secrets in approved secret management.
- Use HTTPS/WSS.
- Add structured logging.
- Add tracing and metrics.
- Add rate limits.
- Validate AudioHook authentication.
- Add call/session state management.
- Add streaming STT/TTS rather than placeholder adapters.
- Add human-transfer integration.
- Add automated tests.
- Follow TCS security and data-retention policies.
