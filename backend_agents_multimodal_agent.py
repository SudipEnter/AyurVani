"""
Multimodal Agent — image / document analysis using Nova 2 Lite
with multimodal inputs and Nova Embeddings for RAG.
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

IMAGE_ANALYSIS_PROMPTS = {
    "tongue": (
        "You are an expert Ayurvedic practitioner performing Jihva Pariksha "
        "(tongue diagnosis). Analyze this tongue image for:\n"
        "- Coating (Ama assessment)\n"
        "- Color (dosha indication)\n"
        "- Shape and size\n"
        "- Markings or cracks\n"
        "Provide Ayurvedic interpretation and recommendations."
    ),
    "skin": (
        "You are an Ayurvedic dermatology expert. Analyze this skin image for:\n"
        "- Skin type (Vata dry / Pitta inflamed / Kapha oily)\n"
        "- Visible conditions\n"
        "- Dosha imbalance indications\n"
        "Suggest Ayurvedic skincare herbs and remedies."
    ),
    "nail": (
        "You are an Ayurvedic practitioner performing Nakha Pariksha "
        "(nail diagnosis). Analyze nails for:\n"
        "- Color and texture\n"
        "- Ridges, spots, or discoloration\n"
        "- Nutritional deficiency indicators\n"
        "Provide dosha-based assessment."
    ),
    "herb": (
        "Identify this medicinal herb / plant and provide:\n"
        "- Common and Sanskrit name\n"
        "- Rasa (taste), Guna (quality), Virya (potency), Vipaka\n"
        "- Medicinal uses in Ayurveda\n"
        "- Dosage and contraindications"
    ),
    "general": (
        "Analyze this health-related image from an Ayurvedic perspective. "
        "Provide observations, potential health indicators, and recommendations."
    ),
}


class MultimodalAgent:
    """Agent for image and document analysis via Nova 2 Lite multimodal."""

    def __init__(self):
        self.bedrock = boto3.client(
            "bedrock-runtime", region_name=settings.aws_region
        )
        self.model_id = settings.nova_lite_model_id
        self.multilingual = MultilingualHelper()

    async def analyze_image(
        self,
        image_bytes: bytes,
        image_content_type: str,
        analysis_type: str = "general",
        language: str = "en",
        additional_context: str = "",
    ) -> Dict[str, Any]:
        """Analyze a health-related image."""

        analysis_prompt = IMAGE_ANALYSIS_PROMPTS.get(
            analysis_type, IMAGE_ANALYSIS_PROMPTS["general"]
        )

        lang_name = self.multilingual.get_language_name(language)

        user_prompt = (
            f"{analysis_prompt}\n\n"
            f"Additional context from patient: {additional_context}\n\n"
            f"Respond in {lang_name}.\n\n"
            "Return JSON:\n"
            '{"analysis": "...", "observations": ["..."], "recommendations": ["..."]}'
        )

        media_type = image_content_type  # e.g. "image/jpeg"

        request_body = {
            "inferenceConfig": {"maxTokens": 2048, "temperature": 0.3},
            "system": [
                {
                    "text": (
                        "You are AyurVani, an Ayurvedic multimodal health analyst. "
                        "Provide detailed yet compassionate analysis. "
                        "Always include a medical disclaimer."
                    )
                }
            ],
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "image": {
                                "format": media_type.split("/")[-1],
                                "source": {
                                    "bytes": base64.b64encode(image_bytes).decode()
                                },
                            }
                        },
                        {"text": user_prompt},
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
            text = result["output"]["message"]["content"][0]["text"]

            try:
                return json.loads(self._extract_json(text))
            except json.JSONDecodeError:
                return {
                    "analysis": text,
                    "observations": [],
                    "recommendations": [],
                }

        except Exception as exc:
            logger.error("multimodal_agent.image_error", error=str(exc))
            raise

    async def analyze_document(
        self,
        doc_bytes: bytes,
        content_type: str,
        language: str = "en",
    ) -> Dict[str, Any]:
        """Analyze a medical document or prescription."""

        lang_name = self.multilingual.get_language_name(language)

        prompt = (
            "Analyze this medical document. Provide:\n"
            "1. Summary of contents\n"
            "2. Ayurvedic perspective on any diagnoses or medications\n"
            "3. Complementary Ayurvedic recommendations\n"
            "4. Any lifestyle modifications suggested by Ayurveda\n\n"
            f"Respond in {lang_name}.\n"
            "Return JSON: "
            '{"summary": "...", "ayurvedic_perspective": "...", "recommendations": ["..."]}'
        )

        # For PDFs / documents, encode as base64 and use document block
        fmt = "pdf" if "pdf" in content_type else "png"

        request_body = {
            "inferenceConfig": {"maxTokens": 2048, "temperature": 0.3},
            "system": [
                {
                    "text": (
                        "You are AyurVani, an Ayurvedic healthcare assistant "
                        "skilled in interpreting medical reports."
                    )
                }
            ],
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "document": {
                                "format": fmt,
                                "source": {
                                    "bytes": base64.b64encode(doc_bytes).decode()
                                },
                            }
                        },
                        {"text": prompt},
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
            text = result["output"]["message"]["content"][0]["text"]

            try:
                return json.loads(self._extract_json(text))
            except json.JSONDecodeError:
                return {
                    "summary": text,
                    "ayurvedic_perspective": "",
                    "recommendations": [],
                }
        except Exception as exc:
            logger.error("multimodal_agent.doc_error", error=str(exc))
            raise

    @staticmethod
    def _extract_json(text: str) -> str:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            return text[start:end]
        return text