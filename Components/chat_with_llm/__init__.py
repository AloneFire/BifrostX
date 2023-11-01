from bifrost.component.base import BaseComponent
from Interfaces.llm_chat.schema import ChatHistory
from Interfaces.llm_chat.interface import Interface as LLL_Chat_Interface
from pydantic import BaseModel
from typing import List


class ApiChatCompletionsInputs(BaseModel):
    messages: List[ChatHistory] = []


class Component(BaseComponent):
    def api_chat_completions(self, inputs: ApiChatCompletionsInputs):
        LLL_Chat_Interface
