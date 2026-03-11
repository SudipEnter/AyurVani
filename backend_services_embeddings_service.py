"""
Multimodal Embeddings service — create and compare embeddings
using Amazon Nova Multimodal Embeddings model.
"""

from __future__ import annotations

import json
import base64
from typing import List, Optional, Union

import boto3
import numpy as np
import structlog

from api.config import settings

logger = structlog.get_logger()


class MultimodalEmbeddingsService:
    """Create embeddings for text, images, and other modalities."""

    def __init__(self):
        self.bedrock = boto3.client(
            "bedrock-runtime", region_name=settings.aws_region
        )
        self.model_id = settings.nova_embed_model_id
        self.dimension = settings.embedding_dimension

    async def create_text_embedding(
        self,
        text: str,
        purpose: str = "RETRIEVAL",
    ) -> List[float]:
        """Create a text embedding."""
        body = {
            "inputText": text,
            "dimensions": self.dimension,
            "embeddingTypes": ["float"],
        }

        try:
            response = self.bedrock.invoke_model(
                body=json.dumps(body),
                modelId=self.model_id,
                accept="application/json",
                contentType="application/json",
            )
            result = json.loads(response["body"].read())
            return result["embedding"]
        except Exception as exc:
            logger.error("embeddings.text_error", error=str(exc))
            raise

    async def create_image_embedding(
        self,
        image_bytes: bytes,
        text_description: Optional[str] = None,
    ) -> List[float]:
        """Create an embedding from an image (optionally with text)."""
        body: dict = {
            "inputImage": base64.b64encode(image_bytes).decode(),
            "dimensions": self.dimension,
            "embeddingTypes": ["float"],
        }

        if text_description:
            body["inputText"] = text_description

        try:
            response = self.bedrock.invoke_model(
                body=json.dumps(body),
                modelId=self.model_id,
                accept="application/json",
                contentType="application/json",
            )
            result = json.loads(response["body"].read())
            return result["embedding"]
        except Exception as exc:
            logger.error("embeddings.image_error", error=str(exc))
            raise

    async def batch_create_embeddings(
        self, texts: List[str]
    ) -> List[List[float]]:
        """Create embeddings for a list of texts."""
        embeddings = []
        for text in texts:
            emb = await self.create_text_embedding(text)
            embeddings.append(emb)
        return embeddings

    @staticmethod
    def cosine_similarity(
        vec_a: List[float], vec_b: List[float]
    ) -> float:
        """Compute cosine similarity between two vectors."""
        a = np.array(vec_a, dtype=np.float32)
        b = np.array(vec_b, dtype=np.float32)
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)