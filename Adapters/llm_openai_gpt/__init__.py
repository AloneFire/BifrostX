from typing import Callable, List
from bifrost.config import Config
from bifrost.utils.logger import logger
from Interfaces.llm_chat import Interface
from pydantic import BaseModel, validate_call, confloat
from enum import Enum
import openai
import json
import tiktoken

from Interfaces.llm_chat.interface import ChatInput, ChatHistory, ChatSSE


class OpenaiApiType(Enum):
    OPENAI = "openai"
    AZURE = "azure"
    AZUREAD = "azuread"


class OpenaiModel(Enum):
    GPT35 = "gpt-3.5-turbo"
    GPT35_16K = "gpt-3.5-turbo-16k"
    GPT4 = "gpt-4"
    GPT4_32K = "gpt-4-32k"


class AdapterConfig(BaseModel):
    gpt_model: OpenaiModel = OpenaiModel.GPT35
    api_base: str = "https://api.openai.com/v1"
    api_type: OpenaiApiType = OpenaiApiType.OPENAI
    api_key: str
    default_temperature: confloat(gt=0, lt=1) = 0.2


class Adapter(Interface):
    @validate_call
    def __init__(self, config: AdapterConfig):
        self.config = config

    @property
    def token_limits(self) -> int:
        if self.config.gpt_model == OpenaiModel.GPT35_16K:
            return 16 * 1024
        elif self.config.gpt_model == OpenaiModel.GPT4_32K:
            return 32 * 1024
        else:
            return 4096

    def calculate_tokens(self, inputs: ChatInput) -> int:
        enc = tiktoken.encoding_for_model(self.config.gpt_model.value)
        messages = [h for h in inputs.history]
        messages.append(ChatHistory(role="user", content=inputs.prompt))
        total = 0
        for msg in messages:
            total += 3 + len(enc.encode(msg.role)) + len(
                enc.encode(msg.content))  # every message follows <|start|>{role/name}\n{content}<|end|>
        total += 3  # every reply is primed with <|start|>assistant<|message|>
        return total

    def _request(self, messages: List[ChatHistory], functions=[], temperature: float = 0, use_stream=False):
        if Config.get("ADAPTER_LLM_OPENAI_GPT_PROXY"):
            openai.proxy = Config.ADAPTER_LLM_OEPNAI_GPT_PROXY
        openai.api_base = self.config.api_base
        openai.api_key = self.config.api_key
        openai.api_type = self.config.api_type.value
        model = self.config.gpt_model.value
        if functions:
            resp = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                functions=functions,
                function_call="auto",
            )
        else:
            resp = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                stream=use_stream,
            )
        return resp

    def _chat(self, inputs: ChatInput, use_stream=False):
        token_count = self.calculate_tokens(inputs)
        if token_count > self.token_limits:
            raise ValueError("请求超出Token最大限制")
        logger.info(f"\nPrompt: {inputs.prompt}\nToken: {token_count}")
        temperature = inputs.temperature if inputs.temperature else self.config.default_temperature
        messages = [h.model_dump() for h in inputs.history]
        messages.append(ChatHistory(role="user", content=inputs.prompt).model_dump())
        resp = self._request(messages=messages, temperature=temperature, use_stream=use_stream)
        return resp

    def chat_with_sse(self, inputs: ChatInput, callback: Callable):
        resp = self._chat(inputs, use_stream=True)
        role = "assistant"
        for chunk in resp:
            if chunk["choices"][0]["delta"].get("role"):
                role = chunk["choices"][0]["delta"]["role"]
            if chunk["choices"][0]["delta"].get("content"):
                content = chunk["choices"][0]["delta"].get("content")
            else:
                content = ""
            result = ChatSSE(event="add", data=ChatHistory(role=role, content=content))
            if chunk["choices"][0]["finish_reason"] == "stop":
                result = ChatSSE(event="finish", data=ChatHistory(role=role, content=content))
            callback(result)

    def chat(self, inputs: ChatInput) -> ChatHistory:
        resp = self._chat(inputs, use_stream=False)
        return ChatHistory(**resp["choices"][0]["message"])