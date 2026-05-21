import json
import uuid
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.apps.chat.engine import chat_query, create_chat_session, get_session_messages, update_rating

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


class ChatRequest(BaseModel):
    session_id: str
    message: str
    language: str = "zh"


class RateRequest(BaseModel):
    rating: int


@router.post("/sessions")
async def new_session():
    session = await create_chat_session(str(uuid.uuid4()), "zh")
    return {"session_id": session.visitor_id}


@router.post("/message")
async def send_message(data: ChatRequest):
    async def event_stream():
        async for event in chat_query(data.session_id, data.message, data.language):
            yield f"event: {event['event']}\ndata: {event['data']}\n\n"
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    return await get_session_messages(session_id)


@router.post("/message/{message_id}/rate")
async def rate_message(message_id: int, data: RateRequest):
    await update_rating(message_id, data.rating)
    return {"ok": True}
