from abc import ABC
from bifrost.config import Config
from pydantic import BaseModel


class BaseInterface(ABC):
    instance_config_schema: BaseModel = None

    def __init__(self, instance_config):
        self.instance_config = self.instance_config_schema(**instance_config)

    @classmethod
    def get_instance(cls, instance_id=None, adapter_name=None):
        if cls.__module__.startswith("Interfaces"):
            from .register import InterfaceRegister
            info = InterfaceRegister.get_interface(cls.__module__)
            return info.get_adapter_instance(adapter_name=adapter_name, instance_id=instance_id)
        else:
            configs = Config.get_extension_config(module=cls.__module__, instances=True)
            if configs:
                if not instance_id:
                    return cls(list(configs.values())[0])
                elif instance_id and instance_id in configs:
                    return cls(configs[instance_id])
            raise ValueError(f"未找到{cls.__module__}实例")
