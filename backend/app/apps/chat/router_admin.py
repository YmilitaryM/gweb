from fastapi import APIRouter, Depends
from sqlalchemy import select, func

from app.apps.auth.router import get_current_user
from app.apps.chat.models import ChatSession, ChatMessage
from app.core.database import async_session

router = APIRouter(
    prefix="/api/v1/admin/chat",
    tags=["admin-chat"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/sessions")
async def list_sessions(page: int = 1, size: int = 20):
    async with async_session() as db:
        total = (await db.execute(select(func.count(ChatSession.id)))).scalar()
        result = await db.execute(
            select(ChatSession).order_by(ChatSession.updated_at.desc()).offset((page-1)*size).limit(size)
        )
        sessions = result.scalars().all()
        return {
            "items": [{"id": s.id, "visitor_id": s.visitor_id, "language": s.language,
                        "created_at": str(s.created_at), "updated_at": str(s.updated_at)} for s in sessions],
            "total": total, "page": page, "size": size,
            "pages": max(1, (total + size - 1) // size)
        }


@router.get("/sessions/{session_id}/messages")
async def get_session_messages_admin(session_id: int):
    async with async_session() as db:
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
        )
        return [{"id": m.id, "role": m.role.value, "content": m.content, "rating": m.rating} for m in result.scalars()]


@router.get("/stats")
async def chat_stats():
    async with async_session() as db:
        total_sessions = (await db.execute(select(func.count(ChatSession.id)))).scalar()
        total_messages = (await db.execute(select(func.count(ChatMessage.id)))).scalar()
        avg_rating = (await db.execute(
            select(func.avg(ChatMessage.rating)).where(ChatMessage.rating.isnot(None))
        )).scalar()
        return {"total_sessions": total_sessions, "total_messages": total_messages, "avg_rating": avg_rating}
