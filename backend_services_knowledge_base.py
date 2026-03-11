"""
Knowledge Base service — manages the Ayurveda vector store
backed by Amazon OpenSearch Serverless.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import boto3
import structlog
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

from api.config import settings

logger = structlog.get_logger()

# ── Ayurveda seed data (loaded on first start) ────────────
SEED_DOCUMENTS = [
    {
        "content": (
            "Triphala is a traditional Ayurvedic formulation consisting of three "
            "fruits: Amalaki (Emblica officinalis), Bibhitaki (Terminalia bellirica), "
            "and Haritaki (Terminalia chebula). It is a Tridoshic Rasayana that "
            "balances Vata, Pitta, and Kapha. Benefits include digestive support, "
            "gentle detoxification, antioxidant protection, and immune enhancement."
        ),
        "source": "Charaka Samhita, Chikitsasthana",
        "metadata": {"category": "formulation", "dosha": "tridosha"},
    },
    {
        "content": (
            "Ashwagandha (Withania somnifera), known as Indian Ginseng, is a premier "
            "Rasayana herb. Rasa: Tikta, Kashaya. Virya: Ushna. Vipaka: Madhura. "
            "It pacifies Vata and Kapha. Used for stress, anxiety, fatigue, low "
            "immunity, and as a general tonic. Standard dose: 3-6g powder with "
            "warm milk. Contraindicated in high Ama and during pregnancy."
        ),
        "source": "Dravyaguna Vijnana",
        "metadata": {"category": "herb", "dosha": "vata-kapha"},
    },
    {
        "content": (
            "Panchakarma is Ayurveda's premier detoxification protocol comprising "
            "five procedures: Vamana (emesis), Virechana (purgation), Basti (enema), "
            "Nasya (nasal therapy), and Raktamokshana (blood-letting). Preceded by "
            "Purvakarma (Snehana — oleation and Swedana — sudation). Recommended "
            "seasonally and for chronic conditions."
        ),
        "source": "Charaka Samhita, Siddhisthana",
        "metadata": {"category": "therapy", "dosha": "tridosha"},
    },
    {
        "content": (
            "Prakriti (constitution) assessment is fundamental in Ayurveda. The "
            "three doshas — Vata (air+ether), Pitta (fire+water), Kapha "
            "(water+earth) — combine in unique proportions at conception. "
            "Assessment considers body frame, skin, hair, appetite, digestion, "
            "sleep patterns, mental tendencies, and emotional disposition."
        ),
        "source": "Ashtanga Hridaya, Sutrasthana",
        "metadata": {"category": "diagnosis", "dosha": "tridosha"},
    },
    {
        "content": (
            "Tulsi (Ocimum sanctum / Holy Basil) is revered as an adaptogenic herb. "
            "Rasa: Tikta, Katu. Virya: Ushna. Vipaka: Katu. "
            "It reduces Kapha and Vata. Benefits: respiratory health, immune support, "
            "stress relief, antimicrobial. Used as fresh leaves, powder, or decoction. "
            "Dose: 3-5g powder or 10-20ml juice daily."
        ),
        "source": "Bhavaprakasha Nighantu",
        "metadata": {"category": "herb", "dosha": "kapha-vata"},
    },
    {
        "content": (
            "Surya Namaskar (Sun Salutation) is a Hatha Yoga sequence of 12 asanas "
            "that stimulates the cardiovascular system, improves flexibility, and "
            "balances all three doshas. Best practiced at sunrise. Particularly "
            "beneficial for Kapha constitution to increase agni (digestive fire)."
        ),
        "source": "Hatha Yoga Pradipika",
        "metadata": {"category": "yoga", "dosha": "tridosha"},
    },
    {
        "content": (
            "Dinacharya (daily routine) is fundamental to Ayurvedic health. Key "
            "practices include: waking before sunrise, tongue scraping (Jihva "
            "Nirlekhana), oil pulling (Gandusha), Abhyanga (self-massage with "
            "warm oil), exercise appropriate to constitution, meditation, and "
            "eating meals at regular times aligned with Agni."
        ),
        "source": "Ashtanga Hridaya, Sutrasthana Ch.2",
        "metadata": {"category": "lifestyle", "dosha": "tridosha"},
    },
    {
        "content": (
            "Siddha medicine, originating in Tamil Nadu, uses the concept of "
            "Mukkutram (three humors: Vatham, Pittham, Kapham). Diagnostic "
            "methods include Envagai Thervu (eight-fold examination): Naa "
            "(tongue), Niram (color), Mozhi (voice), Vizhi (eyes), Sparisam "
            "(touch), Malam (stool), Neer (urine), Naadi (pulse)."
        ),
        "source": "Siddha Medical Literature",
        "metadata": {"category": "siddha", "dosha": "tridosha"},
    },
    {
        "content": (
            "Chyawanprash is a traditional Ayurvedic jam (Avaleha) with Amalaki as "
            "its primary ingredient, combined with over 40 herbs. It is a potent "
            "Rasayana for immunity, respiratory health, and vitality. Suitable for "
            "all ages and constitutions. Typical dose: 1-2 teaspoons daily with "
            "warm milk."
        ),
        "source": "Charaka Samhita, Chikitsasthana Ch.1",
        "metadata": {"category": "formulation", "dosha": "tridosha"},
    },
    {
        "content": (
            "Nadi Pariksha (pulse diagnosis) is the most refined Ayurvedic "
            "diagnostic technique. The Vaidya feels the radial pulse at three "
            "finger positions corresponding to Vata (index), Pitta (middle), "
            "and Kapha (ring finger). Pulse quality reveals organ health, "
            "dosha imbalances, tissue conditions, and mental state."
        ),
        "source": "Yoga Ratnakara",
        "metadata": {"category": "diagnosis", "dosha": "tridosha"},
    },
]


class KnowledgeBaseService:
    """Manage the Ayurveda knowledge vector store."""

    def __init__(self):
        self.index_name = "ayurvani-knowledge"
        self._client: Optional[OpenSearch] = None
        self._initialized = False

    async def initialize(self):
        """Connect to OpenSearch and seed data if needed."""
        if self._initialized:
            return

        try:
            if settings.opensearch_endpoint:
                credentials = boto3.Session().get_credentials()
                awsauth = AWS4Auth(
                    credentials.access_key,
                    credentials.secret_key,
                    settings.aws_region,
                    "aoss",
                    session_token=credentials.token,
                )
                self._client = OpenSearch(
                    hosts=[{"host": settings.opensearch_endpoint, "port": 443}],
                    http_auth=awsauth,
                    use_ssl=True,
                    verify_certs=True,
                    connection_class=RequestsHttpConnection,
                    timeout=30,
                )
                await self._ensure_index()
                logger.info("knowledge_base.connected")
            else:
                logger.warning(
                    "knowledge_base.no_endpoint",
                    message="Running with in-memory fallback",
                )
                self._in_memory_store: List[Dict] = []

            self._initialized = True

        except Exception as exc:
            logger.error("knowledge_base.init_error", error=str(exc))
            self._in_memory_store = []
            self._initialized = True

    async def _ensure_index(self):
        """Create the vector index if it doesn't exist."""
        if self._client and not self._client.indices.exists(self.index_name):
            body = {
                "settings": {
                    "index": {
                        "knn": True,
                        "knn.algo_param.ef_search": 512,
                    }
                },
                "mappings": {
                    "properties": {
                        "content": {"type": "text"},
                        "source": {"type": "keyword"},
                        "metadata": {"type": "object"},
                        "embedding": {
                            "type": "knn_vector",
                            "dimension": settings.embedding_dimension,
                            "method": {
                                "name": "hnsw",
                                "space_type": "cosinesimil",
                                "engine": "nmslib",
                            },
                        },
                    }
                },
            }
            self._client.indices.create(self.index_name, body=body)
            logger.info("knowledge_base.index_created")

    async def ingest(
        self,
        content: str,
        embedding: List[float],
        source: str,
        metadata: Optional[Dict] = None,
    ):
        """Insert a document with its embedding."""
        doc = {
            "content": content,
            "source": source,
            "metadata": metadata or {},
            "embedding": embedding,
        }

        if self._client:
            self._client.index(index=self.index_name, body=doc)
        else:
            self._in_memory_store.append(doc)

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """k-NN search for similar documents."""
        if self._client:
            body = {
                "size": top_k,
                "query": {
                    "knn": {
                        "embedding": {
                            "vector": query_embedding,
                            "k": top_k,
                        }
                    }
                },
            }
            try:
                resp = self._client.search(index=self.index_name, body=body)
                return [
                    {
                        "content": hit["_source"]["content"],
                        "source": hit["_source"]["source"],
                        "score": hit["_score"],
                        "metadata": hit["_source"].get("metadata", {}),
                    }
                    for hit in resp["hits"]["hits"]
                ]
            except Exception as exc:
                logger.error("knowledge_base.search_error", error=str(exc))
                return self._fallback_search(query_embedding, top_k)
        else:
            return self._fallback_search(query_embedding, top_k)

    def _fallback_search(
        self, query_embedding: List[float], top_k: int
    ) -> List[Dict[str, Any]]:
        """Brute-force cosine search on in-memory store (dev/demo only)."""
        import numpy as np

        if not hasattr(self, "_in_memory_store") or not self._in_memory_store:
            # Return seed data as fallback
            return [
                {
                    "content": doc["content"],
                    "source": doc["source"],
                    "score": 0.75,
                    "metadata": doc["metadata"],
                }
                for doc in SEED_DOCUMENTS[:top_k]
            ]

        q = np.array(query_embedding, dtype=np.float32)
        scored = []
        for doc in self._in_memory_store:
            d = np.array(doc["embedding"], dtype=np.float32)
            denom = np.linalg.norm(q) * np.linalg.norm(d)
            sim = float(np.dot(q, d) / denom) if denom else 0.0
            scored.append((sim, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "content": doc["content"],
                "source": doc["source"],
                "score": score,
                "metadata": doc.get("metadata", {}),
            }
            for score, doc in scored[:top_k]
        ]