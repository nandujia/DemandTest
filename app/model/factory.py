from .types import ModelConfig
from .providers import OpenAICompletionsClient, AnthropicMessagesClient


class ModelFactory:
    @classmethod
    def create(cls, config: ModelConfig):
        api = (config.api or "").strip().lower()
        if api == "anthropic-messages":
            return AnthropicMessagesClient(config)
        return OpenAICompletionsClient(config)

