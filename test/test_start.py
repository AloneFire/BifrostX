from bifrostx.utils.logger import logger
from bifrostx.config import Config
from bifrostx.initialization import init_extension_dir
from Interfaces.llm_chat.interface import Interface
from Adapters.llm_openai_gpt import Adapter

init_extension_dir()
instance = Interface.get_instance(adapter_name="llm_zhipu_glm")
# instance = Adapter.get_instance()
print(instance)
if instance:
    for data in instance.chat_with_stream(
        prompt=[{"role": "user", "content": "请讲一个高级的笑话"}], temperature=0.9
    ):
        print(data.content, end="")
