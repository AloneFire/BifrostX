from bifrost.interface.base import BaseInterface
from abc import abstractmethod
from pydantic import BaseModel, confloat, constr, field_validator
from typing import Optional, List


class ChatHistory(BaseModel):
    role: constr(pattern=r"^(system|user|assistant)$")
    content: str


class ChatInputs(BaseModel):
    prompt: List[ChatHistory]
    temperature: Optional[confloat(gt=0, lt=1)] = None
    top_p: Optional[confloat(gt=0, lt=1)] = None

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, value:List[ChatHistory]):
        if value and value[-1].role == "user":
            return value
        raise ValueError("prompt must end with a user message")

