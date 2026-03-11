"""Pydantic schemas for API requests and responses."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────────
class Language(str, Enum):
    EN = "en"
    HI = "hi"
    TA = "ta"
    TE = "te"
    KN = "kn"
    ML = "ml"
    BN = "bn"
    MR = "mr"
    GU = "gu"
    PA = "pa"
    OR = "or"
    UR = "ur"
    SA = "sa"


class Dosha(str, Enum):
    VATA = "vata"
    PITTA = "pitta"
    KAPHA = "kapha"
    VATA_PITTA = "vata-pitta"
    PITTA_KAPHA = "pitta-kapha"
    VATA_KAPHA = "vata-kapha"
    TRIDOSHA = "tridosha"


class ConsultationType(str, Enum):
    INITIAL = "initial"
    FOLLOW_UP = "follow_up"
    SYMPTOM_CHECK = "symptom_check"
    DIET_ADVICE = "diet_advice"
    YOGA_GUIDANCE = "yoga_guidance"


# ── Request Models ─────────────────────────────────────────
class ConsultationRequest(BaseModel):
    """Start or continue a text consultation."""

    user_id: str = Field(..., min_length=1, max_length=128)
    session_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=5000)
    language: Language = Language.EN
    consultation_type: ConsultationType = ConsultationType.INITIAL
    context: Optional[Dict[str, Any]] = None


class SymptomAnalysisRequest(BaseModel):
    """Analyze symptoms with optional image."""

    user_id: str
    symptoms: List[str] = Field(..., min_items=1)
    duration: Optional[str] = None
    severity: Optional[int] = Field(None, ge=1, le=10)
    language: Language = Language.EN
    medical_history: Optional[str] = None


class DoshaAssessmentRequest(BaseModel):
    """Prakriti (constitution) assessment."""

    user_id: str
    responses: Dict[str, str] = Field(
        ..., description="Question-answer pairs from Prakriti questionnaire"
    )
    language: Language = Language.EN


class ImageAnalysisRequest(BaseModel):
    """Analyze a health-related image."""

    user_id: str
    analysis_type: str = Field(
        ..., description="tongue, skin, nail, or general"
    )
    language: Language = Language.EN
    additional_context: Optional[str] = None


class EmbeddingSearchRequest(BaseModel):
    """Search the knowledge base."""

    query: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(5, ge=1, le=20)
    content_type: str = "text"


# ── Response Models ────────────────────────────────────────
class ConsultationResponse(BaseModel):
    session_id: str
    response: str
    recommendations: Optional[List[str]] = None
    follow_up_questions: Optional[List[str]] = None
    dosha_indication: Optional[Dosha] = None
    confidence: float = Field(ge=0.0, le=1.0)
    language: Language
    timestamp: datetime


class SymptomAnalysisResponse(BaseModel):
    session_id: str
    analysis: str
    possible_imbalances: List[str]
    recommended_herbs: List[HerbRecommendation]
    dietary_suggestions: List[str]
    yoga_recommendations: List[str]
    severity_assessment: str
    disclaimer: str
    language: Language


class HerbRecommendation(BaseModel):
    name: str
    sanskrit_name: Optional[str] = None
    benefits: str
    dosage: Optional[str] = None
    contraindications: Optional[List[str]] = None
    source: Optional[str] = None


class DoshaAssessmentResponse(BaseModel):
    primary_dosha: Dosha
    secondary_dosha: Optional[Dosha] = None
    prakriti_description: str
    characteristics: List[str]
    dietary_guidelines: List[str]
    lifestyle_recommendations: List[str]
    language: Language


class VoiceConsultationResponse(BaseModel):
    session_id: str
    transcript: str
    response_text: str
    audio_url: Optional[str] = None
    language: Language
    duration_seconds: float


class SearchResult(BaseModel):
    content: str
    source: str
    score: float
    metadata: Dict[str, Any] = {}


class EmbeddingSearchResponse(BaseModel):
    results: List[SearchResult]
    query: str
    total_results: int


# Rebuild models with forward refs
SymptomAnalysisResponse.model_rebuild()