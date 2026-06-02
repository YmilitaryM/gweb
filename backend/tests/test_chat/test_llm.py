import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_factory_returns_error_without_api_key(monkeypatch):
    """When no API key is configured, factory should raise ValueError."""
    from app.config import settings
    monkeypatch.setattr(settings, "llm_mock", "")
    with patch("app.apps.chat.llm._get_db_setting", new=AsyncMock(return_value="")):
        from app.apps.chat.llm import get_llm_provider
        with pytest.raises(ValueError, match="No LLM API key configured"):
            await get_llm_provider()


@pytest.mark.asyncio
async def test_factory_returns_openai_provider(monkeypatch):
    """Factory returns OpenAIProvider when configured."""
    from app.config import settings
    monkeypatch.setattr(settings, "llm_mock", "")
    async def mock_get(key, default=""):
        mapping = {
            "llm_provider": "openai",
            "llm_api_key": "sk-test123",
            "llm_model": "gpt-4o",
        }
        return mapping.get(key, default)

    with patch("app.apps.chat.llm._get_db_setting", new=mock_get):
        from app.apps.chat.llm import get_llm_provider
        from app.apps.chat.llm.openai import OpenAIProvider
        provider = await get_llm_provider()
        assert isinstance(provider, OpenAIProvider)


@pytest.mark.asyncio
async def test_factory_returns_deepseek_provider(monkeypatch):
    """Factory returns DeepSeekProvider when configured."""
    from app.config import settings
    monkeypatch.setattr(settings, "llm_mock", "")
    async def mock_get(key, default=""):
        mapping = {
            "llm_provider": "deepseek",
            "llm_api_key": "sk-test123",
            "llm_model": "deepseek-chat",
        }
        return mapping.get(key, default)

    with patch("app.apps.chat.llm._get_db_setting", new=mock_get):
        from app.apps.chat.llm import get_llm_provider
        from app.apps.chat.llm.deepseek import DeepSeekProvider
        provider = await get_llm_provider()
        assert isinstance(provider, DeepSeekProvider)


@pytest.mark.asyncio
async def test_factory_returns_anthropic_provider(monkeypatch):
    """Factory returns AnthropicProvider when configured."""
    from app.config import settings
    monkeypatch.setattr(settings, "llm_mock", "")
    async def mock_get(key, default=""):
        mapping = {
            "llm_provider": "anthropic",
            "llm_api_key": "sk-ant-test123",
            "llm_model": "claude-sonnet-4-6",
        }
        return mapping.get(key, default)

    with patch("app.apps.chat.llm._get_db_setting", new=mock_get):
        from app.apps.chat.llm import get_llm_provider
        from app.apps.chat.llm.anthropic import AnthropicProvider
        provider = await get_llm_provider()
        assert isinstance(provider, AnthropicProvider)


@pytest.mark.asyncio
async def test_factory_applies_settings_to_global(monkeypatch):
    """Factory updates global settings object with DB values."""
    from app.config import settings
    monkeypatch.setattr(settings, "llm_mock", "")
    async def mock_get(key, default=""):
        mapping = {
            "llm_provider": "openai",
            "llm_api_key": "sk-override",
            "llm_model": "gpt-4-turbo",
            "embedding_provider": "deepseek",
            "embedding_api_key": "sk-emb",
            "embedding_model": "custom-emb",
        }
        return mapping.get(key, default)

    from app.config import settings
    with patch("app.apps.chat.llm._get_db_setting", new=mock_get):
        from app.apps.chat.llm import get_llm_provider
        await get_llm_provider()
        assert settings.llm_provider == "openai"
        assert settings.llm_api_key == "sk-override"
        assert settings.llm_model == "gpt-4-turbo"
        assert settings.embedding_provider == "deepseek"
        assert settings.embedding_api_key == "sk-emb"
        assert settings.embedding_model == "custom-emb"
