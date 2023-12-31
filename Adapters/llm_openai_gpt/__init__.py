from typing import List, Optional
from bifrostx.config import Config
from Interfaces.llm_chat import Interface
from bifrostx.core.data_model import BaseModel, validate_call, confloat
from enum import Enum
import openai
import tiktoken
from Interfaces.llm_chat import ChatInputs, ChatHistory, ChatOutputs, ChatTokenUsage


class OpenaiApiType(Enum):
    OPENAI = "openai"
    AZURE = "azure"
    AZUREAD = "azuread"


class OpenaiModel(Enum):
    GPT35 = "gpt-3.5-turbo"
    GPT35_16K = "gpt-3.5-turbo-16k"
    GPT4 = "gpt-4"
    GPT4_32K = "gpt-4-32k"


class AdapterInstanceConfig(BaseModel):
    ai_model: OpenaiModel = OpenaiModel.GPT35
    api_base: str = "https://api.openai.com/v1"
    api_type: OpenaiApiType = OpenaiApiType.OPENAI
    api_key: str
    default_temperature: confloat(gt=0, lt=1) = 0.2


class Adapter(Interface):
    instance_config_schema = AdapterInstanceConfig

    def __init__(self, instance_config: AdapterInstanceConfig):
        super().__init__(instance_config)
        self.config = Config.get_extension_config(__name__)

    @property
    def token_limits(self) -> int:
        if self.instance_config.ai_model == OpenaiModel.GPT35_16K:
            return 16 * 1024
        elif self.instance_config.ai_model == OpenaiModel.GPT4_32K:
            return 32 * 1024
        else:
            return 4096

    def calculate_tokens(self, messages: List[ChatHistory]) -> int:
        enc = tiktoken.encoding_for_model(self.instance_config.ai_model.value)
        total = 0
        for msg in messages:
            total += (
                3 + len(enc.encode(msg.role)) + len(enc.encode(msg.content))
            )  # every message follows <|start|>{role/name}\n{content}<|end|>
        total += 3  # every reply is primed with <|start|>assistant<|message|>
        return total

    def _request(
        self,
        messages: List[ChatHistory],
        functions=[],
        temperature: float = 0,
        use_stream=False,
    ):
        if self.config.get("proxy"):
            openai.proxy = self.config.get("proxy")
        openai.api_base = self.instance_config.api_base
        openai.api_key = self.instance_config.api_key
        openai.api_type = self.instance_config.api_type.value
        model = self.instance_config.ai_model.value
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

    def _chat(self, inputs: ChatInputs, use_stream=False):
        token_count = self.calculate_tokens(inputs.prompt)
        if token_count > self.token_limits:
            raise ValueError("请求超出Token最大限制")
        temperature = (
            inputs.temperature
            if inputs.temperature
            else self.instance_config.default_temperature
        )
        messages = [h.model_dump() for h in inputs.prompt]
        resp = self._request(
            messages=messages, temperature=temperature, use_stream=use_stream
        )
        return resp

    @validate_call
    def chat(
        self,
        prompt: List[ChatHistory],
        temperature: Optional[confloat(gt=0, lt=1)] = None,
        top_p: Optional[confloat(gt=0, lt=1)] = None,
    ) -> ChatOutputs:
        inputs = ChatInputs(prompt=prompt, temperature=temperature, top_p=top_p)
        resp = self._chat(inputs, use_stream=False)
        usage = ChatTokenUsage(
            inputs=resp.usage.prompt_tokens,
            outputs=resp.usage.completion_tokens,
            total=resp.usage.total_tokens,
        )
        message = ChatHistory(
            role=resp.choices[0].message.role, content=resp.choices[0].message.content
        )
        return ChatOutputs(message=message, usage=usage)

    @validate_call
    def chat_with_stream(
        self,
        prompt: List[ChatHistory],
        temperature: Optional[confloat(gt=0, lt=1)] = None,
        top_p: Optional[confloat(gt=0, lt=1)] = None,
    ) -> ChatOutputs:
        inputs = ChatInputs(prompt=prompt, temperature=temperature, top_p=top_p)
        resp = self._chat(inputs, use_stream=True)
        role = "assistant"
        usage = ChatTokenUsage()
        usage.inputs = self.calculate_tokens(inputs.prompt)
        for chunk in resp:
            if chunk["choices"][0]["delta"].get("role"):
                role = chunk["choices"][0]["delta"]["role"]
            if chunk["choices"][0]["delta"].get("content"):
                content = chunk["choices"][0]["delta"].get("content")
            else:
                content = ""
            result = ChatHistory(role=role, content=content)
            usage.outputs += self.calculate_tokens([result])
            usage.total = usage.inputs + usage.outputs
            yield ChatOutputs(message=result, usage=usage)
