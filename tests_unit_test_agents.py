"""Unit tests for voice and multimodal agents."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json


class TestVoiceAgent:
    @pytest.mark.asyncio
    async def test_process_voice_calls_bedrock(self):
        with patch("boto3.client") as mock_client:
            mock_bedrock = MagicMock()
            mock_client.return_value = mock_bedrock

            mock_response_body = MagicMock()
            mock_response_body.read.return_value = json.dumps({
                "inputTranscript": "I have a headache",
                "output": {
                    "message": {
                        "content": [{"text": "For headaches, try Brahmi oil massage."}]
                    }
                },
            }).encode()

            mock_bedrock.invoke_model.return_value = {"body": mock_response_body}

            from agents.voice_agent import VoiceAgent

            agent = VoiceAgent()
            result = await agent.process_voice(
                audio_bytes=b"\x00" * 16000,
                language="en",
                session_id="test",
                user_id="test-user",
            )

            assert result["transcript"] == "I have a headache"
            assert "Brahmi" in result["response_text"]


class TestMultimodalAgent:
    @pytest.mark.asyncio
    async def test_analyze_image_calls_bedrock(self):
        with patch("boto3.client") as mock_client:
            mock_bedrock = MagicMock()
            mock_client.return_value = mock_bedrock

            mock_response_body = MagicMock()
            mock_response_body.read.return_value = json.dumps({
                "output": {
                    "message": {
                        "content": [
                            {
                                "text": '{"analysis": "Tongue shows Ama coating", "observations": ["White coat"], "recommendations": ["Triphala"]}'
                            }
                        ]
                    }
                }
            }).encode()

            mock_bedrock.invoke_model.return_value = {"body": mock_response_body}

            from agents.multimodal_agent import MultimodalAgent

            agent = MultimodalAgent()
            result = await agent.analyze_image(
                image_bytes=b"\xff\xd8\xff\xe0",
                image_content_type="image/jpeg",
                analysis_type="tongue",
                language="en",
            )

            assert "analysis" in result
            assert "Ama" in result["analysis"]