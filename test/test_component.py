from Components.chat_with_llm import Component, ComponentConfig
from Interfaces.llm_chat.interface import Interface as LLL_Chat_Interface
from bifrostx.initialization import init_extension_dir
from fastapi.routing import APIRoute
from bifrostx.utils.logger import logger
from bifrostx.config import Config
from typing import Callable

init_extension_dir()
instacnce_congfig = ComponentConfig(llm_chat_instance=LLL_Chat_Interface.get_instance())
component = Component(instacnce_congfig)

print([func for func in dir(Component) if func.startswith("api_")])
