from typing import List, Optional

import httpx

from .base import BaseModelClient
from .types import Message, MessageRole, ModelConfig


class OpenAICompletionsClient(BaseModelClient):
    def __init__(self, config: ModelConfig):
        self.config = config

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        if self.config.extra and isinstance(self.config.extra.get("headers"), dict):
            headers.update(self.config.extra["headers"])
        return headers

    def chat(self, messages: List[Message], **kwargs) -> str:
        url = f"{self.config.base_url.rstrip('/')}/chat/completions"
        payload = {
            "model": self.config.model.id,
            "messages": [m.to_dict() for m in messages],
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }
        if self.config.extra and isinstance(self.config.extra.get("payload"), dict):
            payload.update(self.config.extra["payload"])
        with httpx.Client(timeout=120.0) as client:
            response = client.post(url, headers=self._headers(), json=payload)
            response.raise_for_status()
            result = response.json()
        return result["choices"][0]["message"]["content"]

    async def achat(self, messages: List[Message], **kwargs) -> str:
        url = f"{self.config.base_url.rstrip('/')}/chat/completions"
        payload = {
            "model": self.config.model.id,
            "messages": [m.to_dict() for m in messages],
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }
        if self.config.extra and isinstance(self.config.extra.get("payload"), dict):
            payload.update(self.config.extra["payload"])
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=self._headers(), json=payload)
            response.raise_for_status()
            result = response.json()
        return result["choices"][0]["message"]["content"]


class AnthropicMessagesClient(BaseModelClient):
    def __init__(self, config: ModelConfig):
        self.config = config

    def _headers(self) -> dict:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.config.api_key or "",
            "anthropic-version": (self.config.extra or {}).get("anthropic_version") or "2023-06-01",
        }
        if self.config.extra and isinstance(self.config.extra.get("headers"), dict):
            headers.update(self.config.extra["headers"])
        return headers

    def _payload(self, messages: List[Message], **kwargs) -> dict:
        system = None
        out: List[dict] = []
        for m in messages:
            if m.role == MessageRole.SYSTEM and system is None:
                system = m.content
                continue
            role = "assistant" if m.role == MessageRole.ASSISTANT else "user"
            out.append({"role": role, "content": m.content})

        payload = {
            "model": self.config.model.id,
            "max_tokens": int(kwargs.get("max_tokens", self.config.max_tokens)),
            "temperature": float(kwargs.get("temperature", self.config.temperature)),
            "messages": out,
        }
        if system:
            payload["system"] = system
        if self.config.extra and isinstance(self.config.extra.get("payload"), dict):
            payload.update(self.config.extra["payload"])
        return payload

    def chat(self, messages: List[Message], **kwargs) -> str:
        url = f"{self.config.base_url.rstrip('/')}/v1/messages"
        with httpx.Client(timeout=120.0) as client:
            response = client.post(url, headers=self._headers(), json=self._payload(messages, **kwargs))
            response.raise_for_status()
            result = response.json()
        content = result.get("content") or []
        if isinstance(content, list) and content and isinstance(content[0], dict):
            return str(content[0].get("text") or "")
        return ""

    async def achat(self, messages: List[Message], **kwargs) -> str:
        url = f"{self.config.base_url.rstrip('/')}/v1/messages"
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=self._headers(), json=self._payload(messages, **kwargs))
            response.raise_for_status()
            result = response.json()
        content = result.get("content") or []
        if isinstance(content, list) and content and isinstance(content[0], dict):
            return str(content[0].get("text") or "")
        return ""

