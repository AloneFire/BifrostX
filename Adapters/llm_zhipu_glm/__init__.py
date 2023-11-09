from typing import List, Optional

from bifrostx.core.data_model import BaseModel, confloat, validate_call
from enum import Enum
from Interfaces.llm_chat import Interface
from Interfaces.llm_chat.schema import (
    ChatInputs,
    ChatHistory,
    ChatOutputs,
    ChatTokenUsage,
)
import zhipuai
import json


class ZhipuaiModel(Enum):
    GLM_Turbo = "chatglm_turbo"


class AdapterInstanceConfig(BaseModel):
    ai_model: ZhipuaiModel = ZhipuaiModel.GLM_Turbo
    default_temperature: confloat(gt=0, lt=1) = 0.2
    default_top_p: confloat(gt=0, lt=1) = 0.7
    api_key: str


class Adapter(Interface):
    instance_config_schema = AdapterInstanceConfig

    def calculate_tokens(self, message: List[ChatHistory]) -> int:
        """
        预测 Token 长度
        """
        return len([h.content for h in message]) / 1.8

    def _chat(self, inputs: ChatInputs, use_stream=False):
        zhipuai.api_key = self.instance_config.api_key
        messages = [h.model_dump() for h in inputs.prompt]
        top_p = inputs.top_p or self.instance_config.default_top_p
        temperature = inputs.temperature or self.instance_config.default_temperature
        if use_stream:
            resp = zhipuai.model_api.sse_invoke(
                model=self.instance_config.ai_model.value,
                prompt=messages,
                temperature=temperature,
                top_p=top_p,
                incremental=True,
            )
        else:
            resp = zhipuai.model_api.invoke(
                model=self.instance_config.ai_model.value,
                prompt=messages,
                temperature=temperature,
                top_p=top_p,
            )
        return resp

    @validate_call
    def chat(
        self,
        prompt: List[ChatHistory],
        temperature: Optional[confloat(gt=0, lt=1)] = None,
        top_p: Optional[confloat(gt=0, lt=1)] = None,
    ) -> ChatHistory:
        inputs = ChatInputs(prompt=prompt, temperature=temperature, top_p=top_p)
        resp = self._chat(inputs)
        usage = ChatTokenUsage(
            inputs=resp["data"]["usage"]["prompt_tokens"],
            outputs=resp["data"]["usage"]["completion_tokens"],
            total=resp["data"]["usage"]["total_tokens"],
        )
        message = ChatHistory(
            role=resp["data"]["choices"][0]["role"],
            content=resp["data"]["choices"][0]["content"],
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
        for event in resp.events():
            usage = ChatTokenUsage(inputs=0, outputs=0, total=0)
            if event.meta:
                meta = json.loads(event.meta)
                if "usage" in meta:
                    usage.inputs = meta["usage"].get("prompt_tokens", 0)
                    usage.outputs = meta["usage"].get("completion_tokens", 0)
                    usage.total = meta["usage"].get("total_tokens", 0)
            message = ChatHistory(role="assistant", content=event.data)
            yield ChatOutputs(message=message, usage=usage)
