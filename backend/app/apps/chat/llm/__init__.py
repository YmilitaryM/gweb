from app.config import settings as env_settings


async def _get_db_setting(key: str, default: str = "") -> str:
    try:
        from app.apps.settings.service import get_setting
        val = await get_setting(key)
        return val if val else default
    except Exception:
        return default


async def get_llm_provider():
    """Factory that reads config from DB at call time. Changes take effect immediately.

    Raises ValueError if no API key is configured (unless GWEB_LLM_MOCK=1 for testing).
    """
    if env_settings.llm_api_key == "mock" or getattr(env_settings, "llm_mock", None) == "1":
        class _MockProvider:
            async def chat_stream(self, messages, **kwargs):
                yield "This is a test mock response."
            async def embed(self, texts):
                return [[0.0] * 1536 for _ in texts]
        return _MockProvider()

    provider_name = await _get_db_setting("llm_provider", env_settings.llm_provider)
    api_key = await _get_db_setting("llm_api_key", env_settings.llm_api_key)
    model = await _get_db_setting("llm_model", env_settings.llm_model)
    emb_provider = await _get_db_setting("embedding_provider", env_settings.embedding_provider)
    emb_api_key = await _get_db_setting("embedding_api_key", env_settings.embedding_api_key)
    emb_model = await _get_db_setting("embedding_model", env_settings.embedding_model)

    if not api_key:
        raise ValueError(
            "No LLM API key configured. Set it via Admin Settings or GWEB_LLM_API_KEY env var."
        )

    # Apply to global settings so providers can access them
    env_settings.llm_provider = provider_name
    env_settings.llm_api_key = api_key
    env_settings.llm_model = model
    env_settings.embedding_provider = emb_provider
    env_settings.embedding_api_key = emb_api_key
    env_settings.embedding_model = emb_model

    provider_name = provider_name.lower()
    if provider_name == "openai":
        from app.apps.chat.llm.openai import OpenAIProvider
        return OpenAIProvider()
    elif provider_name == "deepseek":
        from app.apps.chat.llm.deepseek import DeepSeekProvider
        return DeepSeekProvider()
    elif provider_name == "anthropic":
        from app.apps.chat.llm.anthropic import AnthropicProvider
        return AnthropicProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}")
