import json
import logging
from app.apps.chat.llm import get_llm_provider
from app.apps.chat.models import ChatSession, ChatMessage
from app.core.database import async_session
from app.core.qdrant import qdrant
from sqlalchemy import select

logger = logging.getLogger(__name__)


async def create_chat_session(visitor_id: str, language: str = "zh") -> ChatSession:
    async with async_session() as db:
        session = ChatSession(visitor_id=visitor_id, language=language)
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session


async def get_session_messages(session_id: str) -> list[dict]:
    async with async_session() as db:
        result = await db.execute(
            select(ChatSession).where(ChatSession.visitor_id == session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            return []
        result2 = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session.id)
            .order_by(ChatMessage.created_at)
        )
        return [
            {"id": m.id, "role": m.role.value, "content": m.content, "sources": m.sources, "rating": m.rating}
            for m in result2.scalars()
        ]


async def save_message(session_id: str, role: str, content: str, sources: dict | None = None):
    async with async_session() as db:
        result = await db.execute(
            select(ChatSession).where(ChatSession.visitor_id == session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            return None
        msg = ChatMessage(
            session_id=session.id,
            role=role,
            content=content,
            sources=sources,
        )
        db.add(msg)
        await db.commit()
        await db.refresh(msg)
        return msg


async def update_rating(message_id: int, rating: int):
    async with async_session() as db:
        msg = await db.get(ChatMessage, message_id)
        if msg:
            msg.rating = rating
            await db.commit()


async def chat_query(session_id: str, question: str, language: str = "zh"):
    # Get LLM provider
    provider = await get_llm_provider()

    # RAG: embed question and search for relevant context
    sources = []
    try:
        vectors = await provider.embed([question])
        results = await qdrant.search_similar(vectors[0], top_k=5, score_threshold=0.7)
        sources = [
            {"title": r["payload"].get("title", ""), "text": r["payload"].get("text", ""), "score": r["score"]}
            for r in results
            if r["payload"].get("language", "zh") == language
        ]
    except Exception as e:
        logger.warning("RAG search failed, proceeding without context: %s", e)

    # Build prompt with context
    if sources:
        context_blocks = [s["text"] for s in sources[:3]]
        context_text = "\n\n---\n\n".join(context_blocks)
        system_prompt = (
            "You are a helpful assistant for a smart building operations company. "
            f"Use the following context to answer questions accurately:\n\n{context_text}"
        )
    else:
        system_prompt = "You are a helpful assistant for a smart building operations company."

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]

    yield {"event": "sources", "data": json.dumps(sources)}

    # Stream response
    full_answer = ""
    async for token in provider.chat_stream(messages):
        full_answer += token
        yield {"event": "token", "data": token}

    yield {"event": "done", "data": ""}

    # Save messages
    await save_message(session_id, "user", question)
    await save_message(session_id, "assistant", full_answer, sources)
