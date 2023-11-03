from bifrost.component.base import BaseComponent
from Interfaces.llm_chat.schema import ChatHistory, ChatInputs
from Interfaces.llm_chat.interface import Interface as LLL_Chat_Interface
from pydantic import BaseModel
from typing import List
from bifrost.config import Config


class ComponentConfig(BaseModel):
    llm_chat_instance_id: str = ""


class ApiChatCompletionsInputs(BaseModel):
    messages: List[ChatHistory]


class Component(BaseComponent):
    def __init__(self, config: ComponentConfig):
        super().__init__(config)
        self.config = Config.get_extension_config(__name__)
        self.llm_chat_instance = LLL_Chat_Interface.get_instance(instance_id=config.llm_chat_instance_id)

    def api_chat_completions(self, inputs: ApiChatCompletionsInputs):
        output = self.llm_chat_instance.chat(prompt=inputs.messages[-1].content, history=inputs.messages[:-1])
        return output

