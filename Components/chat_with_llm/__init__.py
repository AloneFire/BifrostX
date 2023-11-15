from bifrostx.component.base import BaseComponent
from Interfaces.llm_chat.schema import ChatHistory, ChatInputs
from Interfaces.llm_chat import Interface as LLMChatInterface
from bifrostx.core.data_model import (
    BaseModel,
    field_validator,
    ValidationInfo,
    ConfigDict,
)
from typing import List, Union
from bifrostx.config import Config
from bifrostx.utils.logger import logger


class ComponentConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    llm_chat_instance: Union[str, LLMChatInterface]

    @field_validator("llm_chat_instance")
    @classmethod
    def validate_llm_chat_instance(cls, v: str, info: ValidationInfo):
        if isinstance(v, str):
            ins = LLMChatInterface.get_instance(instance_id=v)
            if ins:
                return ins
            raise ValueError(f"{info.field_name}: llm_chat instance not found")
        return v


class ApiChatCompletionsInputs(BaseModel):
    messages: List[ChatHistory]


class Component(BaseComponent):
    instance_config_schema = ComponentConfig

    def api_chat_completions(self, inputs: ApiChatCompletionsInputs):
        logger.info(f"Prompt: {inputs.messages}")
        output = self.instance_config.llm_chat_instance.chat(prompt=inputs.messages)
        logger.info(f"Output: {output.message}")
        return output
