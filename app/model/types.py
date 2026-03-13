from enum import Enum
from typing import Dict, Optional, List, Any

from pydantic import BaseModel


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    role: MessageRole
    content: str

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role.value, "content": self.content}


class ModelInfo(BaseModel):
    id: str
    name: str


class ModelConfig(BaseModel):
    provider: str
    base_url: str
    api: str
    api_key: str = ""
    model: ModelInfo
    temperature: float = 0.7
    max_tokens: int = 4096
    extra: Optional[Dict[str, Any]] = None

