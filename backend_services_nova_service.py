"""
Nova Lite service — thin wrapper around Bedrock invoke for
text-only generation with Amazon Nova 2 Lite.
"""

from __future__ import annotations

import json
from typing import List, Optional

import boto3
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from api.config import settings

logger = structlog.get_logger()


class NovaLiteService:
    """Invoke Amazon Nova 2 Lite for text generation."""

    def __init__(self):
        self.bedrock = boto3.client(
            "bedrock-runtime", region_name=settings.aws_region
        )
        self.model_id = settings.nova_lite_model_id

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def generate(
        self,
        user_prompt: str,
        system_prompt: str = "",
        max_tokens: int = 2048,
        temperature: float = 0.4,
        top_p: float = 0.9,
        stop_sequences: Optional[List[str]] = None,
    ) -> str:
        """Generate text with Nova 2 Lite."""

        messages = [{"role": "user", "content": [{"text": user_prompt}]}]

        body: dict = {
            "inferenceConfig": {
                "maxTokens": max_tokens,
                "temperature": temperature,
                "topP": top_p,
            },
            "messages": messages,
        }

        if system_prompt:
            body["system"] = [{"text": system_prompt}]

        if stop_sequences:
            body["inferenceConfig"]["stopSequences"] = stop_sequences

        try:
            response = self.bedrock.invoke_model(
                body=json.dumps(body),
                modelId=self.model_id,
                accept="application/json",
                contentType="application/json",
            )

            result = json.loads(response["body"].read())
            output_text = result["output"]["message"]["content"][0]["text"]

            logger.info(
                "nova_lite.generate",
                input_tokens=result.get("usage", {}).get("inputTokens"),
                output_tokens=result.get("usage", {}).get("outputTokens"),
            )

            return output_text

        except Exception as exc:
            logger.error("nova_lite.error", error=str(exc))
            raise

    async def assess_dosha(
        self, responses: dict, language: str
    ) -> dict:
        """Run a Prakriti assessment based on questionnaire answers."""

        prompt = f"""
Based on the following Prakriti assessment questionnaire responses, determine
the patient's constitutional type (Prakriti).

RESPONSES:
{json.dumps(responses, indent=2, ensure_ascii=False)}

Analyze each response to identify Vata, Pitta, and Kapha characteristics.
Provide percentages and determine primary and secondary dosha.

Respond in {language} with JSON:
{{
  "primary_dosha": "vata | pitta | kapha",
  "secondary_dosha": "vata | pitta | kapha | null",
  "prakriti_description": "Detailed description of their constitution",
  "characteristics": ["characteristic 1", "characteristic 2", "..."],
  "dietary_guidelines": ["guideline 1", "guideline 2"],
  "lifestyle_recommendations": ["recommendation 1", "recommendation 2"]
}}
"""

        raw = await self.generate(
            system_prompt=(
                "You are an expert Ayurvedic Vaidya specializing in Prakriti analysis."
            ),
            user_prompt=prompt,
            temperature=0.2,
        )

        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            return json.loads(raw[start:end])
        except (json.JSONDecodeError, ValueError):
            return {
                "primary_dosha": "tridosha",
                "secondary_dosha": None,
                "prakriti_description": raw,
                "characteristics": [],
                "dietary_guidelines": [],
                "lifestyle_recommendations": [],
            }