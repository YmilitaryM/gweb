from app.config import settings


class QdrantService:
    def __init__(self):
        self.url = settings.qdrant_url
        self.collection = settings.qdrant_collection

    async def ensure_collection(self):
        pass  # Real impl creates collection; mock does nothing

    async def upsert_points(self, points: list[dict]):
        pass  # points: list of {"id": str, "vector": list[float], "payload": dict}

    async def search_similar(self, vector: list[float], top_k: int = 5, score_threshold: float = 0.7) -> list[dict]:
        return []  # Returns list of {"id": ..., "score": ..., "payload": ...}

    async def delete_by_filter(self, content_id: int, content_type: str):
        pass


qdrant = QdrantService()
