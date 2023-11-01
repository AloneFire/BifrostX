from bifrost.interface.base import BaseInterface
from abc import abstractmethod
from .schema import *


class Interface(BaseInterface):
    @property
    def token_limits(self) -> int:
        """
        Token 长度限制
        """
        return 4096

    def calculate_tokens(self, inputs: ChatInput) -> int:
        """
        预测 Token 长度
        """
        return len(inputs.prompt)

    @abstractmethod
    def chat(self, inputs: ChatInput) -> ChatHistory:
        """
        对话
        """
        return NotImplemented

    @abstractmethod
    def chat_with_stream(self, inputs: ChatInput) -> ChatHistory:
        """
        对话，SSE流式结果返回
        """
        return NotImplemented
