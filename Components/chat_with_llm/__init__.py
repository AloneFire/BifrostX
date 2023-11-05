from bifrost.component.base import BaseComponent
from Interfaces.llm_chat.schema import ChatHistory, ChatInputs
from Interfaces.llm_chat.interface import Interface as LLL_Chat_Interface
from pydantic import BaseModel, InstanceOf
from typing import List
from bifrost.config import Config


class ComponentConfig(BaseModel):
    llm_chat_instance: InstanceOf[LLL_Chat_Interface]

class ApiChatCompletionsInputs(BaseModel):
    messages: List[ChatHistory]


class Component(BaseComponent):
    def __init__(self, config: ComponentConfig):
        super().__init__(config)
        self.instance_config = config
        self.config = Config.get_extension_config(__name__)

    def api_chat_completions(self, inputs: ApiChatCompletionsInputs):
        output = self.instance_config.llm_chat_instance.chat(prompt=inputs.messages)
        return output

