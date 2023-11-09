from Interfaces.llm_chat import (
    ChatHistory,
    Interface,
    List,
    Optional,
    confloat,
    ChatOutputs,
    ChatTokenUsage,
    ChatInputs,
)
from bifrostx.core.data_model import BaseModel, validate_call
import dashscope
from enum import Enum


class DashscopeModel(Enum):
    bailian_v1 = "bailian-v1"
    dolly_12b_v2 = "dolly-12b-v2"
    qwen_turbo = "qwen-turbo"
    qwen_plus = "qwen-plus"


class AdapterInstanceConfig(BaseModel):
    api_key: str
    ai_model: DashscopeModel = DashscopeModel.qwen_turbo
    default_temperature: confloat(gt=0, lt=1) = 0.2
    default_top_p: confloat(gt=0, lt=1) = 0.7


class Adapter(Interface):
    instance_config_schema = AdapterInstanceConfig

    @property
    def token_limits(self) -> int:
        return 8192

    def _chat(self, inputs: ChatInputs, use_stream: bool = False):
        messages = [m.model_dump() for m in inputs.prompt]
        response = dashscope.Generation.call(
            model=self.instance_config.ai_model.value,
            messages=messages,
            api_key=self.instance_config.api_key,
            temperature=inputs.temperature
            if inputs.temperature
            else self.instance_config.default_temperature,
            top_p=inputs.top_p if inputs.top_p else self.instance_config.default_top_p,
            stream=use_stream,
            incremental_output=use_stream,
        )
        return response

    @validate_call
    def chat(
        self,
        prompt: List[ChatHistory],
        temperature: Optional[confloat(gt=0, lt=1)] = None,
        top_p: Optional[confloat(gt=0, lt=1)] = None,
    ) -> ChatOutputs:
        inputs = ChatInputs(prompt=prompt, temperature=temperature, top_p=top_p)
        resp = self._chat(inputs)
        message = ChatHistory(
            role="assistant",
            content=resp.output.text,
        )
        usage = ChatTokenUsage(
            inputs=resp.usage.input_tokens,
            outputs=resp.usage.output_tokens,
            total=resp.usage.total_tokens,
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
        for chunk in resp:
            message = ChatHistory(
                role="assistant",
                content=chunk.output.text,
            )
            usage = ChatTokenUsage(
                inputs=chunk.usage.input_tokens,
                outputs=chunk.usage.output_tokens,
                total=chunk.usage.total_tokens,
            )
            yield ChatOutputs(message=message, usage=usage)
