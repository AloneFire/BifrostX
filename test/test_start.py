from bifrost.utils.logger import logger
from bifrost.config import Config
from bifrost.initialization import init_extension_dir
from bifrost.interface.register import InterfaceRegister
logger.info("init extension dir")
init_extension_dir()
info = InterfaceRegister.get_interface("llm_chat")
print(info.profile)
print(info.adapters)
print(info.interface)
# adapter_instance_configs = list(Config.get_extension_config(Adapter.__module__, instances=True).values())
# instance_config = AdapterInstanceConfig(**adapter_instance_configs[0])
# instance = Adapter(instance_config)
# for data in instance.chat_with_stream({
#     "prompt": "请讲一个高级的笑话"
# }):
#     print(data.content, end="")
