from pydantic import BaseModel
from bifrostx.interface.base import BaseInterface
from bifrostx.utils.logger import logger
from .profile import AdapterProfile
from typing import Dict, List, Type
from bifrostx.config import Config


class AdapterInfo(BaseModel):
    module_name: str
    adapter: Type[BaseInterface]
    profile: AdapterProfile

    @property
    def instance_configs(self):
        instances_configs = Config.get_extension_config(
            f"Adapters.{self.module_name}", instances=True
        )
        return instances_configs


class AdapterRegister:
    adapters: Dict[str, BaseInterface] = {}

    @classmethod
    def register(cls, module_name):
        try:
            from bifrostx.interface.register import InterfaceRegister

            profile = AdapterProfile.load_by_module_name(module_name)
            adapter = profile.load_enter_class()
            adapter_info = AdapterInfo(
                module_name=module_name, adapter=adapter, profile=profile
            )
            cls.adapters[module_name] = adapter_info
            for interface_module_name in profile.implements:
                if interface_module_name.interface not in InterfaceRegister.interfaces:
                    raise ValueError(
                        f"没有找到依赖的Interface({interface_module_name.interface})"
                    )
                InterfaceRegister.interfaces[interface_module_name.interface].adapters[
                    module_name
                ] = adapter_info
            logger.info(f"Load Adapter [{module_name}] Success")
        except Exception as ex:
            logger.warning(f"Load Adapter [{module_name}] Error: {ex}")

    @classmethod
    def get_adapters(cls) -> List[AdapterInfo]:
        return list(cls.adapters.values())
