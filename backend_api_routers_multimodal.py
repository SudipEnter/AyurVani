"""Multimodal router — image / document analysis & embedding search."""

import base64
from uuid import uuid4

import structlog
from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Request

from api.models.schemas import (
    EmbeddingSearchRequest,
    EmbeddingSearchResponse,
    ImageAnalysisRequest,
    Language,
    SearchResult,
)
from agents.multimodal_agent import MultimodalAgent
from services.embeddings_service import MultimodalEmbeddingsService

logger = structlog.get_logger()
router = APIRouter()

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB


# ── Image Analysis ─────────────────────────────────────────
@router.post("/analyze-image")
async def analyze_image(
    image: UploadFile = File(...),
    analysis_type: str = Form("general"),
    language: Language = Form(Language.EN),
    user_id: str = Form(...),
    additional_context: str = Form(""),
):
    """
    Analyze a health-related image (tongue, skin, nail, herbs)
    using Nova multimodal capabilities.
    """
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, and WebP images are accepted")

    image_bytes = await image.read()
    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=413, detail="Image too large (max 5 MB)")

    logger.info("multimodal.analyze_image", user_id=user_id, type=analysis_type)

    try:
        agent = MultimodalAgent()
        result = await agent.analyze_image(
            image_bytes=image_bytes,
            image_content_type=image.content_type,
            analysis_type=analysis_type,
            language=language.value,
            additional_context=additional_context,
        )

        return {
            "session_id": str(uuid4()),
            "analysis": result["analysis"],
            "observations": result.get("observations", []),
            "recommendations": result.get("recommendations", []),
            "language": language,
            "disclaimer": (
                "This AI analysis is for educational purposes only. "
                "Please consult a qualified Ayurvedic practitioner for diagnosis."
            ),
        }
    except Exception as exc:
        logger.error("multimodal.image_error", error=str(exc))
        raise HTTPException(status_code=500, detail="Image analysis failed") from exc


# ── Document Analysis ──────────────────────────────────────
@router.post("/analyze-document")
async def analyze_document(
    document: UploadFile = File(...),
    language: Language = Form(Language.EN),
    user_id: str = Form(...),
):
    """Analyze a medical document or prescription."""
    doc_bytes = await document.read()
    if len(doc_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Document too large (max 10 MB)")

    logger.info("multimodal.analyze_doc", user_id=user_id)

    try:
        agent = MultimodalAgent()
        result = await agent.analyze_document(
            doc_bytes=doc_bytes,
            content_type=document.content_type,
            language=language.value,
        )

        return {
            "session_id": str(uuid4()),
            "summary": result["summary"],
            "ayurvedic_perspective": result.get("ayurvedic_perspective", ""),
            "recommendations": result.get("recommendations", []),
            "language": language,
        }
    except Exception as exc:
        logger.error("multimodal.doc_error", error=str(exc))
        raise HTTPException(status_code=500, detail="Document analysis failed") from exc


# ── Knowledge Base Search ──────────────────────────────────
@router.post("/search", response_model=EmbeddingSearchResponse)
async def search_knowledge_base(
    req: EmbeddingSearchRequest,
    request: Request,
):
    """Semantic search across the Ayurveda knowledge base using Nova Multimodal Embeddings."""
    logger.info("multimodal.search", query=req.query[:80])

    try:
        embeddings_svc = MultimodalEmbeddingsService()
        kb = request.app.state.knowledge_base

        query_embedding = await embeddings_svc.create_text_embedding(req.query)
        results = await kb.search(query_embedding, top_k=req.top_k)

        return EmbeddingSearchResponse(
            results=[
                SearchResult(
                    content=r["content"],
                    source=r["source"],
                    score=r["score"],
                    metadata=r.get("metadata", {}),
                )
                for r in results
            ],
            query=req.query,
            total_results=len(results),
        )
    except Exception as exc:
        logger.error("multimodal.search_error", error=str(exc))
        raise HTTPException(status_code=500, detail="Search failed") from exc