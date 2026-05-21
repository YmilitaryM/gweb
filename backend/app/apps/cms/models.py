from sqlalchemy import String, Integer, BigInteger, ForeignKey, Boolean, JSON, Enum as SAEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.models import Base, TimestampMixin
import enum


class MediaType(str, enum.Enum):
    image = "image"
    video = "video"
    document = "document"


class Media(Base, TimestampMixin):
    __tablename__ = "media"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    type: Mapped[MediaType] = mapped_column(SAEnum(MediaType), nullable=False)
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    alt_text_zh: Mapped[str | None] = mapped_column(String(500), nullable=True)
    alt_text_en: Mapped[str | None] = mapped_column(String(500), nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True)


class Page(Base, TimestampMixin):
    __tablename__ = "pages"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_zh: Mapped[str] = mapped_column(String(200), nullable=False)
    name_en: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    blocks: Mapped[list["Block"]] = relationship(
        "Block", back_populates="page", order_by="Block.order",
        cascade="all, delete-orphan"
    )


class Block(Base, TimestampMixin):
    __tablename__ = "blocks"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    page_id: Mapped[int] = mapped_column(ForeignKey("pages.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    content: Mapped[dict] = mapped_column(JSON, default=dict)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    page: Mapped["Page"] = relationship("Page", back_populates="blocks")


class Menu(Base, TimestampMixin):
    __tablename__ = "menus"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("menus.id", ondelete="SET NULL"), nullable=True)
    name_zh: Mapped[str] = mapped_column(String(100), nullable=False)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    link: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)
    location: Mapped[str] = mapped_column(String(20), nullable=False, default="header")
    parent: Mapped["Menu | None"] = relationship("Menu", remote_side=[id], back_populates="children")
    children: Mapped[list["Menu"]] = relationship("Menu", back_populates="parent")
