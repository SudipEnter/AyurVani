"""
Voice Agent — wraps Nova 2 Sonic for speech-to-speech Ayurvedic consultation.
"""

from __future__ import annotations

import base64
import json
from typing import Any, Dict, Optional

import boto3
import structlog

from api.config import settings
from utils.multilingual import MultilingualHelper

logger = structlog.get_logger()

VOICE_SYSTEM_PROMPT = """\
You are AyurVani, a warm and knowledgeable Ayurvedic healthcare voice assistant.

Speak naturally and compassionately.  Keep answers concise (2-4 sentences)
unless the patient asks for detail.  When you recommend herbs, slowly spell
any Sanskrit names so the patient can note them down.

Always remind the patient that your guidance is educational and they should
consult a qualified Ayurvedic practitioner for serious concerns.

Respond in the patient's language.
"""


class VoiceAgent:
    """Agent that manages Nova 2 Sonic interactions."""

    def __init__(self):
        self.bedrock = boto3.client(
            "bedrock-runtime", region_name=settings.aws_region
        )
        self.model_id = settings.nova_sonic_model_id
        self.multilingual = MultilingualHelper()
        self._conversation_history: Dict[str, list] = {}

    # ── Full audio file processing ─────────────────────────
    async def process_voice(
        self,
        audio_bytes: bytes,
        language: str,
        session_id: str,
        user_id: str,
    ) -> Dict[str, Any]:
        """Process a complete audio recording through Nova Sonic."""

        system_prompt = (
            VOICE_SYSTEM_PROMPT
            + f"\n\nRespond in {self.multilingual.get_language_name(language)}."
        )

        request_body = {
            "inferenceConfig": {
                "maxTokens": 1024,
                "temperature": 0.5,
            },
            "system": [{"text": system_prompt}],
            "messages": self._get_history(session_id)
            + [
                {
                    "role": "user",
                    "content": [
                        {
                            "audio": {
                                "format": "wav",
                                "source": {
                                    "bytes": base64.b64encode(audio_bytes).decode()
                                },
                            }
                        }
                    ],
                }
            ],
        }

        try:
            response = self.bedrock.invoke_model(
                body=json.dumps(request_body),
                modelId=self.model_id,
                accept="application/json",
                contentType="application/json",
            )

            result = json.loads(response["body"].read())

            transcript = result.get("inputTranscript", "")
            response_text = ""
            response_audio = None

            for block in result.get("output", {}).get("message", {}).get("content", []):
                if "text" in block:
                    response_text += block["text"]
                if "audio" in block:
                    response_audio = base64.b64decode(block["audio"]["source"]["bytes"])

            # Update conversation memory
            self._add_to_history(session_id, "user", transcript)
            self._add_to_history(session_id, "assistant", response_text)

            return {
                "transcript": transcript,
                "response_text": response_text,
                "response_audio": response_audio,
                "audio_url": None,  # Set if stored to S3
                "duration_seconds": len(audio_bytes) / (16000 * 2),  # 16 kHz 16-bit
            }

        except Exception as exc:
            logger.error("voice_agent.invoke_error", error=str(exc))
            raise

    # ── Streaming chunk processing ─────────────────────────
    async def process_voice_chunk(
        self,
        audio_chunk: bytes,
        language: str,
        session_id: str,
    ) -> Dict[str, Any]:
        """Process a single audio chunk (used in WebSocket streaming)."""

        system_prompt = (
            VOICE_SYSTEM_PROMPT
            + f"\n\nRespond in {self.multilingual.get_language_name(language)}."
        )

        request_body = {
            "inferenceConfig": {
                "maxTokens": 512,
                "temperature": 0.5,
            },
            "system": [{"text": system_prompt}],
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "audio": {
                                "format": "pcm",
                                "source": {
                                    "bytes": base64.b64encode(audio_chunk).decode()
                                },
                                "sampleRate": 16000,
                            }
                        }
                    ],
                }
            ],
        }

        try:
            response = self.bedrock.invoke_model_with_response_stream(
                body=json.dumps(request_body),
                modelId=self.model_id,
                accept="application/json",
                contentType="application/json",
            )

            partial_text = ""
            response_audio = b""

            for event in response.get("body", []):
                chunk = json.loads(event["chunk"]["bytes"])
                if "text" in chunk:
                    partial_text += chunk["text"]
                if "audio" in chunk:
                    response_audio += base64.b64decode(chunk["audio"])

            return {
                "partial_text": partial_text,
                "response_text": partial_text,
                "response_audio": response_audio if response_audio else None,
            }

        except Exception as exc:
            logger.error("voice_agent.stream_error", error=str(exc))
            return {"partial_text": "", "response_audio": None}

    # ── Conversation memory ────────────────────────────────
    def _get_history(self, session_id: str) -> list:
        return self._conversation_history.get(session_id, [])

    def _add_to_history(self, session_id: str, role: str, text: str):
        if session_id not in self._conversation_history:
            self._conversation_history[session_id] = []
        self._conversation_history[session_id].append(
            {"role": role, "content": [{"text": text}]}
        )
        # Keep last 10 turns
        self._conversation_history[session_id] = self._conversation_history[
            session_id
        ][-20:]