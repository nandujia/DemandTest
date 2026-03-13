from abc import ABC, abstractmethod
from typing import List, Optional

from .types import Message


class BaseModelClient(ABC):
    @abstractmethod
    def chat(self, messages: List[Message], **kwargs) -> str:
        raise NotImplementedError()

    @abstractmethod
    async def achat(self, messages: List[Message], **kwargs) -> str:
        raise NotImplementedError()

    def chat_with_context(self, messages: List[Message], context: str, **kwargs) -> str:
        return self.chat(messages, **kwargs)

