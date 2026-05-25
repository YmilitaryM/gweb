import logging
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from app.config import settings

logger = logging.getLogger(__name__)


class QdrantService:
    def __init__(self):
        self.url = settings.qdrant_url
        self.collection = settings.qdrant_collection
        self._client: QdrantClient | None = None
        self._available: bool | None = None

    def _get_client(self) -> QdrantClient | None:
        if self._client is None:
            try:
                self._client = QdrantClient(url=self.url, timeout=10)
            except Exception:
                self._available = False
                return None
        return self._client

    async def _is_available(self) -> bool:
        if self._available is not None:
            return self._available
        client = self._get_client()
        if client is None:
            self._available = False
            return False
        try:
            client.get_collections()
            self._available = True
        except Exception:
            logger.warning("Qdrant unavailable at %s, RAG disabled", self.url)
            self._available = False
        return self._available

    async def ensure_collection(self):
        if not await self._is_available():
            return
        client = self._get_client()
        try:
            client.get_collection(self.collection)
        except Exception:
            client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )

    async def upsert_points(self, points: list[dict]):
        if not await self._is_available():
            return
        client = self._get_client()
        client.upsert(
            collection_name=self.collection,
            points=[
                PointStruct(id=p["id"], vector=p["vector"], payload=p.get("payload", {}))
                for p in points
            ],
        )

    async def search_similar(
        self, vector: list[float], top_k: int = 5, score_threshold: float = 0.7
    ) -> list[dict]:
        if not await self._is_available():
            return []
        client = self._get_client()
        results = client.search(
            collection_name=self.collection,
            query_vector=vector,
            limit=top_k,
            score_threshold=score_threshold,
        )
        return [
            {"id": r.id, "score": r.score, "payload": r.payload}
            for r in results
        ]

    async def delete_by_filter(self, content_id: int, content_type: str):
        if not await self._is_available():
            return
        client = self._get_client()
        client.delete(
            collection_name=self.collection,
            points_selector=Filter(
                must=[
                    FieldCondition(key="content_id", match=MatchValue(value=content_id)),
                    FieldCondition(key="content_type", match=MatchValue(value=content_type)),
                ]
            ),
        )


qdrant = QdrantService()
