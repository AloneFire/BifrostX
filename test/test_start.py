from bifrost.utils.logger import logger
from bifrost.config import Config
from bifrost.initialization import init_extension_dir
from bifrost.interface.register import InterfaceRegister
from Interfaces.llm_chat.interface import Interface
from Adapters.llm_openai_gpt import Adapter

init_extension_dir()
# interface_info = InterfaceRegister.get_interface("llm_chat")
# instance = interface_info.get_adapter_instance()
# instance.get_instance()
instance = Interface.get_instance(adapter_name="llm_zhipu_glm")
# instance = Adapter.get_instance()
print(instance)
for data in instance.chat_with_stream(prompt=[{"role": "user", "content": "请讲一个高级的笑话"}]):
    print(data.content, end="")
