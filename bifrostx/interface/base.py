from abc import ABC
from bifrostx.config import Config
from pydantic import BaseModel
from bifrostx.utils.logger import logger
from typing import Type


class BaseInterface(ABC):
    instance_config_schema: Type[BaseModel] = None

    def __init__(self, instance_config):
        self.instance_config = (
            self.instance_config_schema(**instance_config)
            if self.instance_config_schema
            else None
        )

    @classmethod
    def get_instance(cls, instance_id=None, adapter_name=None):
        try:
            if cls.__module__.startswith("Interfaces"):
                from .register import InterfaceRegister

                info = InterfaceRegister.get_interface(cls.__module__)
                if info:
                    return info.get_adapter_instance(
                        adapter_name=adapter_name, instance_id=instance_id
                    )
                raise ValueError(f"未找到{cls.__module__}实例")
            else:
                configs = Config.get_extension_config(
                    module=cls.__module__, instances=True
                )
                if configs:
                    if not instance_id:
                        return cls(list(configs.values())[0])
                    elif instance_id and instance_id in configs:
                        return cls(configs[instance_id])
                raise ValueError(f"未找到{cls.__module__}实例")
        except ValueError as ex:
            logger.warning(ex)
            return None
