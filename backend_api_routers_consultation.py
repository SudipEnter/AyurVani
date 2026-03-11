"""Consultation router — text-based Ayurvedic consultations."""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request

from api.models.schemas import (
    ConsultationRequest,
    ConsultationResponse,
    DoshaAssessmentRequest,
    DoshaAssessmentResponse,
    SymptomAnalysisRequest,
    SymptomAnalysisResponse,
)
from agents.ayurveda_agent import AyurvedaAgent
from services.nova_service import NovaLiteService

logger = structlog.get_logger()
router = APIRouter()


def _get_agent() -> AyurvedaAgent:
    return AyurvedaAgent()


def _get_nova() -> NovaLiteService:
    return NovaLiteService()


# ── Text Consultation ──────────────────────────────────────
@router.post("/chat", response_model=ConsultationResponse)
async def text_consultation(
    req: ConsultationRequest,
    request: Request,
    agent: AyurvedaAgent = Depends(_get_agent),
):
    """Conduct a text-based Ayurvedic consultation."""
    session_id = req.session_id or str(uuid4())

    logger.info(
        "consultation.start",
        user_id=req.user_id,
        session_id=session_id,
        language=req.language,
    )

    try:
        result = await agent.consult(
            message=req.message,
            session_id=session_id,
            user_id=req.user_id,
            language=req.language.value,
            consultation_type=req.consultation_type.value,
            context=req.context,
            knowledge_base=request.app.state.knowledge_base,
        )

        return ConsultationResponse(
            session_id=session_id,
            response=result["response"],
            recommendations=result.get("recommendations"),
            follow_up_questions=result.get("follow_up_questions"),
            dosha_indication=result.get("dosha_indication"),
            confidence=result.get("confidence", 0.85),
            language=req.language,
            timestamp=datetime.now(timezone.utc),
        )
    except Exception as exc:
        logger.error("consultation.error", error=str(exc))
        raise HTTPException(status_code=500, detail="Consultation failed") from exc


# ── Symptom Analysis ───────────────────────────────────────
@router.post("/symptoms", response_model=SymptomAnalysisResponse)
async def analyze_symptoms(
    req: SymptomAnalysisRequest,
    request: Request,
    agent: AyurvedaAgent = Depends(_get_agent),
):
    """Analyze symptoms using Ayurvedic diagnostic principles."""
    session_id = str(uuid4())

    logger.info(
        "symptoms.analyze",
        user_id=req.user_id,
        symptom_count=len(req.symptoms),
    )

    try:
        result = await agent.analyze_symptoms(
            symptoms=req.symptoms,
            duration=req.duration,
            severity=req.severity,
            medical_history=req.medical_history,
            language=req.language.value,
            knowledge_base=request.app.state.knowledge_base,
        )

        return SymptomAnalysisResponse(
            session_id=session_id,
            **result,
            language=req.language,
        )
    except Exception as exc:
        logger.error("symptoms.error", error=str(exc))
        raise HTTPException(status_code=500, detail="Symptom analysis failed") from exc


# ── Dosha Assessment ───────────────────────────────────────
@router.post("/dosha-assessment", response_model=DoshaAssessmentResponse)
async def assess_dosha(
    req: DoshaAssessmentRequest,
    nova: NovaLiteService = Depends(_get_nova),
):
    """Determine Prakriti (constitutional type) from questionnaire answers."""
    session_id = str(uuid4())

    logger.info("dosha.assess", user_id=req.user_id)

    try:
        result = await nova.assess_dosha(
            responses=req.responses,
            language=req.language.value,
        )

        return DoshaAssessmentResponse(**result, language=req.language)
    except Exception as exc:
        logger.error("dosha.error", error=str(exc))
        raise HTTPException(status_code=500, detail="Assessment failed") from exc


# ── Consultation History ───────────────────────────────────
@router.get("/history/{user_id}")
async def get_history(user_id: str, limit: int = 20):
    """Retrieve consultation history for a user."""
    # In production this reads from DynamoDB
    return {
        "user_id": user_id,
        "consultations": [],
        "message": "History endpoint — connect DynamoDB for persistence",
    }