from bifrost.component.base import BaseComponent
from Interfaces.llm_chat.schema import ChatHistory, ChatInputs
from Interfaces.llm_chat.interface import Interface as LLL_Chat_Interface
from bifrost.core.data_model import BaseModel, InstanceOf
from typing import List
from bifrost.config import Config


class ComponentConfig(BaseModel):
    llm_chat_instance: str


class ApiChatCompletionsInputs(BaseModel):
    messages: List[ChatHistory]


class Component(BaseComponent):
    instance_config_schema = ComponentConfig

    @property
    def llm_chat_instance(self):
        instance = LLL_Chat_Interface.get_instance(
            self.instance_config.llm_chat_instance
        )
        if instance is None:
            raise Exception("LLM Chat instance not found")
        return instance

    def api_chat_completions(self, inputs: ApiChatCompletionsInputs):
        output = self.llm_chat_instance.chat(prompt=inputs.messages)
        return output
