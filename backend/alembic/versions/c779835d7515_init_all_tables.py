"""init_all_tables

Revision ID: c779835d7515
Revises:
Create Date: 2026-05-21 17:28:40.795451

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c779835d7515'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Create ENUM types
    sa.Enum('admin', 'editor', name='userrole').create(op.get_bind())
    sa.Enum('image', 'video', 'document', name='mediatype').create(op.get_bind())
    sa.Enum('user', 'assistant', name='messagerole').create(op.get_bind())

    # --- Table: settings (KV store) ---
    op.create_table(
        'settings',
        sa.Column('key', sa.String(100), primary_key=True),
        sa.Column('value', sa.Text, nullable=False, server_default=''),
        sa.Column('is_encrypted', sa.Boolean, nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- Table: users ---
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('username', sa.String(100), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', postgresql.ENUM('admin', 'editor', name='userrole', create_type=False), nullable=False,
                  server_default='editor'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- Table: media ---
    op.create_table(
        'media',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('original_name', sa.String(255), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('size', sa.BigInteger, nullable=False),
        sa.Column('type', postgresql.ENUM('image', 'video', 'document', name='mediatype', create_type=False),
                  nullable=False),
        sa.Column('path', sa.String(500), nullable=False),
        sa.Column('thumbnail_path', sa.String(500), nullable=True),
        sa.Column('alt_text_zh', sa.String(500), nullable=True),
        sa.Column('alt_text_en', sa.String(500), nullable=True),
        sa.Column('width', sa.Integer, nullable=True),
        sa.Column('height', sa.Integer, nullable=True),
        sa.Column('duration', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- Table: pages ---
    op.create_table(
        'pages',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name_zh', sa.String(200), nullable=False),
        sa.Column('name_en', sa.String(200), nullable=False),
        sa.Column('slug', sa.String(200), unique=True, nullable=False),
        sa.Column('is_published', sa.Boolean, nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- Table: menus ---
    op.create_table(
        'menus',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('parent_id', sa.Integer, sa.ForeignKey('menus.id'), nullable=True),
        sa.Column('name_zh', sa.String(100), nullable=False),
        sa.Column('name_en', sa.String(100), nullable=False),
        sa.Column('link', sa.String(500), nullable=False, server_default=''),
        sa.Column('icon', sa.String(100), nullable=True),
        sa.Column('order', sa.Integer, nullable=False, server_default=sa.text('0')),
        sa.Column('is_visible', sa.Boolean, nullable=False, server_default=sa.text('true')),
        sa.Column('location', sa.String(20), nullable=False, server_default='header'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- Table: news_articles ---
    op.create_table(
        'news_articles',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('title_zh', sa.String(500), nullable=False),
        sa.Column('title_en', sa.String(500), nullable=False),
        sa.Column('summary_zh', sa.String(1000), nullable=False, server_default=''),
        sa.Column('summary_en', sa.String(1000), nullable=False, server_default=''),
        sa.Column('content_zh', sa.Text, nullable=False, server_default=''),
        sa.Column('content_en', sa.Text, nullable=False, server_default=''),
        sa.Column('cover_image_id', sa.Integer, sa.ForeignKey('media.id'), nullable=True),
        sa.Column('category', sa.String(50), nullable=False, server_default='company_news'),
        sa.Column('published_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('is_published', sa.Boolean, nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- Table: blocks ---
    op.create_table(
        'blocks',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('page_id', sa.Integer, sa.ForeignKey('pages.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('order', sa.Integer, nullable=False, server_default=sa.text('0')),
        sa.Column('config', postgresql.JSON, nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column('content', postgresql.JSON, nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column('is_published', sa.Boolean, nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- Table: themes ---
    op.create_table(
        'themes',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(100), unique=True, nullable=False),
        sa.Column('variables', postgresql.JSON, nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column('tech_effects', postgresql.JSON, nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- Table: faqs ---
    op.create_table(
        'faqs',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('question_zh', sa.String(1000), nullable=False),
        sa.Column('question_en', sa.String(1000), nullable=False),
        sa.Column('answer_zh', sa.Text, nullable=False, server_default=''),
        sa.Column('answer_en', sa.Text, nullable=False, server_default=''),
        sa.Column('order', sa.Integer, nullable=False, server_default=sa.text('0')),
        sa.Column('is_published', sa.Boolean, nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- Table: inquiries ---
    op.create_table(
        'inquiries',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('company_name', sa.String(200), nullable=False),
        sa.Column('contact_name', sa.String(100), nullable=False),
        sa.Column('phone', sa.String(50), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('is_read', sa.Boolean, nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- Table: chat_sessions ---
    op.create_table(
        'chat_sessions',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('visitor_id', sa.String(100), unique=True, nullable=False),
        sa.Column('language', sa.String(5), nullable=False, server_default='zh'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- Table: chat_messages ---
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('session_id', sa.Integer, sa.ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', postgresql.ENUM('user', 'assistant', name='messagerole', create_type=False), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('sources', postgresql.JSON, nullable=True),
        sa.Column('rating', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Create indexes
    op.create_index('idx_news_articles_published_at', 'news_articles', ['published_at'])
    op.create_index('idx_news_articles_category', 'news_articles', ['category'])
    op.create_index('idx_blocks_page_id', 'blocks', ['page_id'])
    op.create_index('idx_chat_messages_session_id', 'chat_messages', ['session_id'])
    op.create_index('idx_inquiries_is_read', 'inquiries', ['is_read'])
    op.create_index('idx_themes_is_active', 'themes', ['is_active'])


def downgrade() -> None:
    """Downgrade schema."""

    # Drop indexes
    op.drop_index('idx_themes_is_active')
    op.drop_index('idx_inquiries_is_read')
    op.drop_index('idx_chat_messages_session_id')
    op.drop_index('idx_blocks_page_id')
    op.drop_index('idx_news_articles_category')
    op.drop_index('idx_news_articles_published_at')

    # Drop tables in reverse dependency order
    op.drop_table('chat_messages')
    op.drop_table('chat_sessions')
    op.drop_table('inquiries')
    op.drop_table('faqs')
    op.drop_table('themes')
    op.drop_table('blocks')
    op.drop_table('news_articles')
    op.drop_table('menus')
    op.drop_table('pages')
    op.drop_table('media')
    op.drop_table('users')
    op.drop_table('settings')

    # Drop ENUM types
    sa.Enum(name='messagerole').drop(op.get_bind())
    sa.Enum(name='mediatype').drop(op.get_bind())
    sa.Enum(name='userrole').drop(op.get_bind())
