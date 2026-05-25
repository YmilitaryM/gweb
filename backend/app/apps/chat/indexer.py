import hashlib
from app.apps.chat.chunker import chunk_news, chunk_faq, chunk_page_block
from app.apps.chat.llm import get_llm_provider
from app.core.qdrant import qdrant


async def index_content(content_type: str, data: dict):
    match content_type:
        case "news":
            chunks = chunk_news(data)
        case "faq":
            chunks = chunk_faq(data)
        case "page_block":
            chunks = chunk_page_block(data)
        case _:
            return
    if not chunks:
        return
    provider = await get_llm_provider()
    texts = [c.text for c in chunks]
    vectors = await provider.embed(texts)
    points = []
    for chunk, vector in zip(chunks, vectors):
        points.append({
            "id": hashlib.md5(chunk.id.encode()).hexdigest(),
            "vector": vector,
            "payload": {
                "content_id": chunk.content_id,
                "content_type": chunk.content_type,
                "title": chunk.title,
                "text": chunk.text,
                "language": chunk.language,
                "page_url": chunk.page_url,
            },
        })
    await qdrant.delete_by_filter(data.get("id", 0), content_type)
    await qdrant.upsert_points(points)
