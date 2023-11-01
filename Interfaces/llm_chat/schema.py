from bifrost.interface.base import BaseInterface
from abc import abstractmethod
from pydantic import BaseModel, confloat
from typing import Optional, List


class ChatHistory(BaseModel):
    role: str
    content: str


class ChatInput(BaseModel):
    prompt: str
    temperature: Optional[confloat(gt=0, lt=1)] = None
    top_p: Optional[confloat(gt=0, lt=1)] = None
    history: List[ChatHistory] = []