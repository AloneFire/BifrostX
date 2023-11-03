from typing import List, Optional

from pydantic import BaseModel, confloat, validate_call
from enum import Enum
from Interfaces.llm_chat.interface import Interface
from Interfaces.llm_chat.schema import ChatInputs, ChatHistory
import zhipuai


class ZhipuaiModel(Enum):
    GLM_Turbo = "chatglm_turbo"


class AdapterInstanceConfig(BaseModel):
    glm_model: ZhipuaiModel = ZhipuaiModel.GLM_Turbo
    default_temperature: confloat(gt=0, lt=1) = 0.2
    default_top_p: confloat(gt=0, lt=1) = 0.7
    api_key: str


class Adapter(Interface):
    instance_config_schema = AdapterInstanceConfig

    def _chat(self, inputs: ChatInputs, use_stream=False):
        zhipuai.api_key = self.instance_config.api_key
        messages = [h.model_dump() for h in inputs.prompt]
        top_p = inputs.top_p or self.instance_config.default_top_p
        temperature = inputs.temperature or self.instance_config.default_temperature
        if use_stream:
            resp = zhipuai.model_api.sse_invoke(
                model=self.instance_config.glm_model.value,
                prompt=messages,
                temperature=temperature,
                top_p=top_p,
                incremental=True
            )
        else:
            resp = zhipuai.model_api.invoke(
                model=self.instance_config.glm_model.value,
                prompt=messages,
                temperature=temperature,
                top_p=top_p,
            )
        return resp


    @validate_call
    def chat(self, prompt: List[ChatHistory], temperature: Optional[confloat(gt=0, lt=1)] = None,
             top_p: Optional[confloat(gt=0, lt=1)] = None) -> ChatHistory:
        inputs = ChatInputs(prompt=prompt, temperature=temperature, top_p=top_p)
        resp = self._chat(inputs)
        return ChatHistory(**resp["data"]["choices"][0])

    @validate_call
    def chat_with_stream(self, prompt: List[ChatHistory], temperature: Optional[confloat(gt=0, lt=1)] = None,
                         top_p: Optional[confloat(gt=0, lt=1)] = None) -> ChatHistory:
        inputs = ChatInputs(prompt=prompt, temperature=temperature, top_p=top_p)
        resp = self._chat(inputs, use_stream=True)
        for event in resp.events():
            yield ChatHistory(role="assistant", content=event.data)
