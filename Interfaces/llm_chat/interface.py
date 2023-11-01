from bifrost.interface.base import BaseInterface
from abc import abstractmethod
from pydantic import BaseModel, confloat
from typing import Optional, List


class ChatHistory(BaseModel):
    role: str
    content: str


class ChatInput(BaseModel):
    prompt: str
    temperature: Optional[confloat(gt=0, lt=1)] = None
    top_p: Optional[confloat(gt=0, lt=1)] = None
    history: List[ChatHistory] = []


class Interface(BaseInterface):
    @property
    def token_limits(self) -> int:
        return 4096

    def calculate_tokens(self, inputs: ChatInput) -> int:
        return len(input.model_dump_json())

    @abstractmethod
    def chat(self, inputs: ChatInput) -> ChatHistory:
        return NotImplemented

    @abstractmethod
    def chat_with_stream(self, inputs: ChatInput) -> ChatHistory:
        return NotImplemented
