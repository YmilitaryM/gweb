from app.config import settings


class MockLLMProvider:
    """Mock provider for testing. Returns canned responses."""

    async def chat_stream(self, messages: list[dict], **kwargs):
        yield "This is a mock response. In production, this would be a real LLM response."

    async def embed(self, texts: list[str]) -> list[list[float]]:
        # Return zero vectors of the expected dimension
        return [[0.0] * 1536 for _ in texts]


def get_llm_provider():
    """Factory function. Returns mock for now, real provider when configured."""
    provider_name = settings.llm_provider
    # For now, always return mock since no API key is configured
    return MockLLMProvider()
