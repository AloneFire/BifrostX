from pydantic import BaseModel
from .base import BaseInterface
from .profile import InterfaceProfile
from typing import Dict, List, Type
from bifrost.utils.logger import logger
from bifrost.adapter.register import AdapterInfo


class InterfaceInfo(BaseModel):
    module_name: str
    interface: Type[BaseInterface]
    profile: InterfaceProfile
    adapters: Dict[str, AdapterInfo] = {}


class InterfaceRegister:
    interfaces: Dict[str, InterfaceInfo] = {}

    @classmethod
    def register(cls, module_name: str):
        try:
            profile = InterfaceProfile.load_by_module_name(module_name)
            interface = profile.load_enter_class()
            cls.interfaces[module_name] = InterfaceInfo(module_name=module_name, interface=interface, profile=profile)
            logger.info(f"Load Interface [{module_name}] Success")
        except Exception as ex:
            logger.warning(f"Load Interface [{module_name}] Error: {ex}")

    @classmethod
    def get_interfaces(cls) -> List[InterfaceInfo]:
        return list(cls.interfaces.values())

    @classmethod
    def get_interface(cls, module_name: str) -> InterfaceInfo:
        return cls.interfaces.get(module_name)
