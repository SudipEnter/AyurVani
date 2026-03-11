"""Voice router — real-time speech consultations via Nova 2 Sonic."""

import io
import base64
from uuid import uuid4
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, File, Form, UploadFile, HTTPException, WebSocket, WebSocketDisconnect

from api.models.schemas import Language, VoiceConsultationResponse
from agents.voice_agent import VoiceAgent

logger = structlog.get_logger()
router = APIRouter()


# ── REST: Upload audio file ────────────────────────────────
@router.post("/consultation", response_model=VoiceConsultationResponse)
async def voice_consultation(
    audio: UploadFile = File(..., description="WAV or PCM audio file"),
    language: Language = Form(Language.EN),
    user_id: str = Form(...),
    session_id: str = Form(None),
):
    """
    Accept an audio file, run it through Nova 2 Sonic for
    speech-to-speech Ayurvedic consultation, return text + audio.
    """
    session_id = session_id or str(uuid4())
    logger.info("voice.consultation", user_id=user_id, session_id=session_id)

    audio_bytes = await audio.read()
    if len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty audio file")
    if len(audio_bytes) > 10 * 1024 * 1024:  # 10 MB limit
        raise HTTPException(status_code=413, detail="Audio file too large (max 10 MB)")

    try:
        agent = VoiceAgent()
        result = await agent.process_voice(
            audio_bytes=audio_bytes,
            language=language.value,
            session_id=session_id,
            user_id=user_id,
        )

        return VoiceConsultationResponse(
            session_id=session_id,
            transcript=result["transcript"],
            response_text=result["response_text"],
            audio_url=result.get("audio_url"),
            language=language,
            duration_seconds=result.get("duration_seconds", 0.0),
        )
    except Exception as exc:
        logger.error("voice.error", error=str(exc))
        raise HTTPException(status_code=500, detail="Voice consultation failed") from exc


# ── WebSocket: Streaming bi-directional voice ──────────────
@router.websocket("/stream")
async def voice_stream(ws: WebSocket):
    """
    WebSocket endpoint for real-time streaming voice consultation.

    Protocol:
      1. Client sends JSON init:  {"user_id": "...", "language": "hi", "session_id": "..."}
      2. Client streams raw PCM audio frames (binary messages).
      3. Server streams back audio frames + periodic JSON text updates.
      4. Either side closes the connection.
    """
    await ws.accept()
    logger.info("voice.ws.connected")

    agent = VoiceAgent()
    session_id = str(uuid4())
    language = "en"
    user_id = "anonymous"

    try:
        # Step 1 — init message
        init = await ws.receive_json()
        user_id = init.get("user_id", user_id)
        language = init.get("language", language)
        session_id = init.get("session_id", session_id)

        logger.info("voice.ws.init", user_id=user_id, language=language)

        await ws.send_json({
            "type": "ready",
            "session_id": session_id,
            "message": "AyurVani voice session started. Please speak.",
        })

        # Step 2 — stream audio
        audio_buffer = io.BytesIO()
        while True:
            message = await ws.receive()

            if "bytes" in message:
                audio_buffer.write(message["bytes"])

                # Process in chunks of ~3 seconds (48 000 samples @ 16 kHz)
                if audio_buffer.tell() >= 96_000:
                    audio_buffer.seek(0)
                    chunk = audio_buffer.read()
                    audio_buffer = io.BytesIO()

                    result = await agent.process_voice_chunk(
                        audio_chunk=chunk,
                        language=language,
                        session_id=session_id,
                    )

                    if result.get("response_audio"):
                        await ws.send_bytes(result["response_audio"])

                    if result.get("partial_text"):
                        await ws.send_json({
                            "type": "partial",
                            "text": result["partial_text"],
                        })

            elif "text" in message:
                data = message["text"]
                if data == "END":
                    # Flush remaining audio
                    audio_buffer.seek(0)
                    remaining = audio_buffer.read()
                    if remaining:
                        result = await agent.process_voice_chunk(
                            audio_chunk=remaining,
                            language=language,
                            session_id=session_id,
                        )
                        if result.get("response_audio"):
                            await ws.send_bytes(result["response_audio"])
                        if result.get("response_text"):
                            await ws.send_json({
                                "type": "final",
                                "text": result["response_text"],
                            })
                    break

    except WebSocketDisconnect:
        logger.info("voice.ws.disconnected", session_id=session_id)
    except Exception as exc:
        logger.error("voice.ws.error", error=str(exc))
        await ws.close(code=1011, reason="Internal error")