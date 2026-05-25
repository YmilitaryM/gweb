import json
import httpx
from app.config import settings
from app.apps.chat.llm.base import LLMProvider


class AnthropicProvider(LLMProvider):
    BASE = "https://api.anthropic.com/v1"

    async def chat_stream(self, messages, **kwargs):
        # Convert OpenAI-format messages to Anthropic format
        system = None
        anthropic_messages = []
        for m in messages:
            if m["role"] == "system":
                system = m["content"]
            else:
                anthropic_messages.append({"role": m["role"], "content": m["content"]})

        body = {
            "model": settings.llm_model,
            "messages": anthropic_messages,
            "max_tokens": kwargs.get("max_tokens", 2048),
            "temperature": kwargs.get("temperature", 0.3),
            "stream": True,
        }
        if system:
            body["system"] = system

        async with httpx.AsyncClient(timeout=60) as client:
            async with client.stream(
                "POST", f"{self.BASE}/messages",
                headers={
                    "x-api-key": settings.llm_api_key,
                    "anthropic-version": "2023-06-01",
                },
                json=body,
            ) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        if data.get("type") == "content_block_delta":
                            delta = data.get("delta", {})
                            if "text" in delta:
                                yield delta["text"]

    async def embed(self, texts):
        # Anthropic doesn't have an embeddings API; fall back to mock
        return [[0.0] * 1536 for _ in texts]
