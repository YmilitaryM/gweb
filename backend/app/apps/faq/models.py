from sqlalchemy import String, Text, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.shared.models import Base, TimestampMixin


class FAQ(Base, TimestampMixin):
    __tablename__ = "faqs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question_zh: Mapped[str] = mapped_column(String(1000), nullable=False)
    question_en: Mapped[str] = mapped_column(String(1000), nullable=False)
    answer_zh: Mapped[str] = mapped_column(Text, nullable=False, default="")
    answer_en: Mapped[str] = mapped_column(Text, nullable=False, default="")
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
