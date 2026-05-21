import json
import httpx
from app.config import settings
from app.apps.chat.llm.base import LLMProvider


class DeepSeekProvider(LLMProvider):
    BASE = "https://api.deepseek.com/v1"

    async def chat_stream(self, messages, **kwargs):
        async with httpx.AsyncClient(timeout=60) as client:
            async with client.stream(
                "POST", f"{self.BASE}/chat/completions",
                headers={"Authorization": f"Bearer {settings.llm_api_key}"},
                json={
                    "model": settings.llm_model,
                    "messages": messages,
                    "temperature": kwargs.get("temperature", 0.3),
                    "max_tokens": kwargs.get("max_tokens", 2048),
                    "stream": True,
                },
            ) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        chunk = json.loads(line[6:])
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        if "content" in delta:
                            yield delta["content"]

    async def embed(self, texts):
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.BASE}/embeddings",
                headers={"Authorization": f"Bearer {settings.llm_api_key}"},
                json={"model": "text-embedding-3-small", "input": texts},
            )
            data = resp.json()
            return [d["embedding"] for d in data["data"]]
