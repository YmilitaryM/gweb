from app.apps.chat.llm.base import LLMProvider


class AnthropicProvider(LLMProvider):
    """Anthropic provider stub. Activated when LLM_API_KEY is configured."""

    async def chat_stream(self, messages, **kwargs):
        yield "This is a mock response. In production, this would be an Anthropic response."

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] * 1536 for _ in texts]
