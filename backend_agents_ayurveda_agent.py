"""
Ayurveda Agent — orchestrates tools and Nova 2 Lite reasoning
for Ayurvedic health consultations.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from services.nova_service import NovaLiteService
from services.embeddings_service import MultimodalEmbeddingsService
from services.knowledge_base import KnowledgeBaseService
from utils.ayurveda_knowledge import AyurvedaKnowledge
from utils.multilingual import MultilingualHelper

logger = structlog.get_logger()


SYSTEM_PROMPT = """\
You are AyurVani, a compassionate and knowledgeable Ayurvedic healthcare assistant.

EXPERTISE:
- Ayurveda (Charaka Samhita, Sushruta Samhita, Ashtanga Hridaya)
- Siddha medicine traditions
- Hatha Yoga therapeutic practices
- Herbal medicine (Dravyaguna Vijnana)
- Panchakarma detoxification therapies
- Prakriti (constitution) analysis
- Dietary therapy (Ahara Vijnana)

GUIDELINES:
1. Always respond in the patient's preferred language.
2. Use compassionate, culturally sensitive language.
3. Ask clarifying questions when symptoms are vague.
4. Provide Ayurvedic perspective alongside general health awareness.
5. Recommend consulting qualified practitioners for serious conditions.
6. Never replace emergency medical advice.
7. Reference classical texts when relevant.
8. Explain Sanskrit/traditional terms in the patient's language.

DISCLAIMER — always include:
"This guidance is educational and based on traditional Ayurvedic principles. \
Please consult a qualified healthcare provider for medical concerns."
"""


class AyurvedaAgent:
    """ReAct-style agent backed by Nova 2 Lite."""

    def __init__(self):
        self.nova = NovaLiteService()
        self.embeddings = MultimodalEmbeddingsService()
        self.knowledge = AyurvedaKnowledge()
        self.multilingual = MultilingualHelper()

    # ── Main consultation ──────────────────────────────────
    async def consult(
        self,
        message: str,
        session_id: str,
        user_id: str,
        language: str = "en",
        consultation_type: str = "initial",
        context: Optional[Dict[str, Any]] = None,
        knowledge_base: Optional[KnowledgeBaseService] = None,
    ) -> Dict[str, Any]:
        """Run a single consultation turn."""

        # 1. Retrieve relevant knowledge
        rag_context = ""
        if knowledge_base:
            rag_context = await self._retrieve_context(message, knowledge_base)

        # 2. Build prompt
        lang_instruction = self.multilingual.get_language_instruction(language)
        consultation_prompt = self._build_consultation_prompt(
            message=message,
            consultation_type=consultation_type,
            rag_context=rag_context,
            lang_instruction=lang_instruction,
            extra_context=context,
        )

        # 3. Call Nova 2 Lite
        raw = await self.nova.generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=consultation_prompt,
            max_tokens=2048,
            temperature=0.4,
        )

        # 4. Parse structured output
        return self._parse_response(raw, language)

    # ── Symptom analysis ───────────────────────────────────
    async def analyze_symptoms(
        self,
        symptoms: List[str],
        duration: Optional[str],
        severity: Optional[int],
        medical_history: Optional[str],
        language: str,
        knowledge_base: Optional[KnowledgeBaseService] = None,
    ) -> Dict[str, Any]:
        """Detailed Ayurvedic symptom analysis."""

        symptom_text = ", ".join(symptoms)
        rag_context = ""
        if knowledge_base:
            rag_context = await self._retrieve_context(symptom_text, knowledge_base)

        prompt = f"""
Analyze the following symptoms using Ayurvedic diagnostic methodology (Roga Nidana):

SYMPTOMS: {symptom_text}
DURATION: {duration or 'Not specified'}
SEVERITY (1-10): {severity or 'Not specified'}
MEDICAL HISTORY: {medical_history or 'None provided'}

REFERENCE KNOWLEDGE:
{rag_context}

Respond in **{self.multilingual.get_language_name(language)}** with this JSON structure:
{{
  "analysis": "Detailed Ayurvedic analysis of the condition",
  "possible_imbalances": ["dosha imbalance 1", "dosha imbalance 2"],
  "recommended_herbs": [
    {{
      "name": "Common name",
      "sanskrit_name": "Sanskrit name",
      "benefits": "How it helps",
      "dosage": "Recommended dosage",
      "contraindications": ["if any"]
    }}
  ],
  "dietary_suggestions": ["suggestion 1", "suggestion 2"],
  "yoga_recommendations": ["asana or pranayama 1", "asana 2"],
  "severity_assessment": "mild / moderate / requires professional attention",
  "disclaimer": "Standard medical disclaimer"
}}
"""
        raw = await self.nova.generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=prompt,
            max_tokens=2500,
            temperature=0.3,
        )

        try:
            return json.loads(self._extract_json(raw))
        except json.JSONDecodeError:
            return {
                "analysis": raw,
                "possible_imbalances": [],
                "recommended_herbs": [],
                "dietary_suggestions": [],
                "yoga_recommendations": [],
                "severity_assessment": "unknown",
                "disclaimer": "Please consult a qualified Ayurvedic practitioner.",
            }

    # ── Private helpers ────────────────────────────────────
    async def _retrieve_context(
        self, query: str, kb: KnowledgeBaseService, top_k: int = 5
    ) -> str:
        """Retrieve relevant passages from the knowledge base."""
        try:
            embedding = await self.embeddings.create_text_embedding(query)
            results = await kb.search(embedding, top_k=top_k)
            passages = [r["content"] for r in results]
            return "\n---\n".join(passages) if passages else ""
        except Exception as exc:
            logger.warning("rag.retrieval_failed", error=str(exc))
            return ""

    def _build_consultation_prompt(
        self,
        message: str,
        consultation_type: str,
        rag_context: str,
        lang_instruction: str,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        ctx_block = ""
        if rag_context:
            ctx_block = f"\nREFERENCE KNOWLEDGE:\n{rag_context}\n"

        extra_block = ""
        if extra_context:
            extra_block = f"\nPATIENT CONTEXT:\n{json.dumps(extra_context, indent=2)}\n"

        return f"""
CONSULTATION TYPE: {consultation_type}
{lang_instruction}
{ctx_block}{extra_block}
PATIENT MESSAGE:
{message}

Respond with JSON:
{{
  "response": "Your compassionate reply in the patient's language",
  "recommendations": ["recommendation 1", "recommendation 2"],
  "follow_up_questions": ["question to clarify the condition"],
  "dosha_indication": "vata / pitta / kapha / null if unknown",
  "confidence": 0.85
}}
"""

    def _parse_response(self, raw: str, language: str) -> Dict[str, Any]:
        try:
            data = json.loads(self._extract_json(raw))
            return data
        except (json.JSONDecodeError, ValueError):
            return {
                "response": raw,
                "recommendations": [],
                "follow_up_questions": [],
                "dosha_indication": None,
                "confidence": 0.5,
            }

    @staticmethod
    def _extract_json(text: str) -> str:
        """Extract JSON block from mixed text."""
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            return text[start:end]
        return text