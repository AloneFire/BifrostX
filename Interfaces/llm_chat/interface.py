from bifrostx.interface.base import BaseInterface
from abc import abstractmethod
from .schema import *
from bifrostx.core.data_model import validate_call


class Interface(BaseInterface):
    @property
    def token_limits(self) -> int:
        """
        Token 长度限制
        """
        return 4096

    def calculate_tokens(self, inputs: ChatInputs) -> int:
        """
        预测 Token 长度
        """
        return len([h.content for h in inputs.prompt])

    @abstractmethod
    def chat(
        self,
        prompt: List[ChatHistory],
        temperature: Optional[confloat(gt=0, lt=1)] = None,
        top_p: Optional[confloat(gt=0, lt=1)] = None,
    ) -> ChatHistory:
        """
        对话
        """
        return NotImplemented

    @abstractmethod
    def chat_with_stream(
        self,
        prompt: List[ChatHistory],
        temperature: Optional[confloat(gt=0, lt=1)] = None,
        top_p: Optional[confloat(gt=0, lt=1)] = None,
    ) -> ChatHistory:
        """
        对话，SSE流式结果返回
        """
        return NotImplemented
