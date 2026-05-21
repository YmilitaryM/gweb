from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.models import Base, TimestampMixin


class NewsArticle(Base, TimestampMixin):
    __tablename__ = "news_articles"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title_zh: Mapped[str] = mapped_column(String(500), nullable=False)
    title_en: Mapped[str] = mapped_column(String(500), nullable=False)
    summary_zh: Mapped[str] = mapped_column(String(1000), default="")
    summary_en: Mapped[str] = mapped_column(String(1000), default="")
    content_zh: Mapped[str] = mapped_column(Text, default="")
    content_en: Mapped[str] = mapped_column(Text, default="")
    cover_image_id: Mapped[int | None] = mapped_column(ForeignKey("media.id"), nullable=True)
    cover_image: Mapped["Media | None"] = relationship("Media", foreign_keys=[cover_image_id])
    category: Mapped[str] = mapped_column(String(50), default="company_news")
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
