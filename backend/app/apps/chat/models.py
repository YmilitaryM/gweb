from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, Integer, JSON, Enum as SAEnum, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.models import Base, TimestampMixin
import enum


class MessageRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"


class ChatSession(Base, TimestampMixin):
    __tablename__ = "chat_sessions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    visitor_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    language: Mapped[str] = mapped_column(String(5), default="zh")
    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage", back_populates="session", order_by="ChatMessage.created_at"
    )


class ChatMessage(Base, TimestampMixin):
    __tablename__ = "chat_messages"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[MessageRole] = mapped_column(SAEnum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sources: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")
