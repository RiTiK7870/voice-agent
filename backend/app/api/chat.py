from fastapi.responses import Response
from app.speech.tts import synthesize_speech
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.speech.stt import transcribe_audio
from pydantic import BaseModel

from app.agent.graph import run_agent


router = APIRouter()


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    source: list[str]
    escalated: bool


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = run_agent(
        request.session_id,
        request.message
    )

    return ChatResponse(
        session_id=request.session_id,
        answer=result["answer"],
        source=result.get("sources", []),
        escalated=result.get("escalated", False),
    )
@router.post("/rag-test")
def rag_test(request: ChatRequest):
    from app.rag.retriever import retrieve

    results = retrieve(request.message, top_k=3)

    return {
        "query": request.message,
        "results": results,
    }

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    audio_bytes = await file.read()

    if not audio_bytes:
        raise HTTPException(
            status_code=400,
            detail="Audio file is empty"
        )

    try:
        transcript = transcribe_audio(audio_bytes)

        return {
            "filename": file.filename,
            "transcript": transcript,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )

@router.post("/voice-chat")
async def voice_chat(session_id: str, file: UploadFile = File(...)):
    audio_bytes = await file.read()

    if not audio_bytes:
        raise HTTPException(
            status_code=400,
            detail="Audio file is empty"
        )

    try:
        # 1. Speech -> Text
        transcript = transcribe_audio(audio_bytes)

        if not transcript.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not detect speech in audio"
            )

        # 2. Text -> LangGraph -> RAG -> Answer
        result = run_agent(
            session_id,
            transcript
        )

        answer = result["answer"]

        # 3. Answer -> Speech
        response_audio = synthesize_speech(answer)

        if not response_audio:
            raise HTTPException(
                status_code=500,
                detail="TTS returned empty audio"
            )

        # 4. Return audio + metadata
        return Response(
            content=response_audio,
            media_type="audio/wav",
            headers={
                "X-Session-ID": session_id,
                "X-Transcript": transcript,
                "X-Answer": answer,
                "X-Escalated": str(
                    result.get("escalated", False)
                ),
                "X-Sources": ",".join(
                    result.get("sources", [])
                ),
            }
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Voice processing failed: {str(e)}"
        )       