from sqlalchemy import String, Text, ForeignKey, Boolean, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.models import Base, TimestampMixin


class Case(Base, TimestampMixin):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_zh: Mapped[str] = mapped_column(String(300), nullable=False)
    name_en: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    cover_image_id: Mapped[int | None] = mapped_column(ForeignKey("media.id"), nullable=True)
    summary_zh: Mapped[str] = mapped_column(Text, nullable=False, default="")
    summary_en: Mapped[str] = mapped_column(Text, nullable=False, default="")
    content_zh: Mapped[str] = mapped_column(Text, nullable=False, default="")
    content_en: Mapped[str] = mapped_column(Text, nullable=False, default="")
    category: Mapped[str] = mapped_column(String(50), default="park")
    stats: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

    cover_image: Mapped["Media | None"] = relationship("Media", foreign_keys=[cover_image_id])
