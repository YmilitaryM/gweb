import json
from app.apps.chat.llm import get_llm_provider
from app.apps.chat.models import ChatSession, ChatMessage
from app.core.database import async_session
from sqlalchemy import select


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
    # Search context (mock — real impl queries Qdrant)
    sources = []

    # Build prompt with context
    system_prompt = "You are a helpful assistant for a smart building operations company."
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]

    # Send sources first
    yield {"event": "sources", "data": json.dumps(sources)}

    # Stream response
    provider = get_llm_provider()
    full_answer = ""
    async for token in provider.chat_stream(messages):
        full_answer += token
        yield {"event": "token", "data": token}

    yield {"event": "done", "data": ""}

    # Save messages
    await save_message(session_id, "user", question)
    await save_message(session_id, "assistant", full_answer, sources)
