from pydantic import BaseModel
from .base import BaseComponent
from bifrost.interface.register import InterfaceRegister, InterfaceInfo
from .profile import ComponentProfile
from typing import Dict, List, Type
from bifrost.utils.logger import logger


class ComponentInfo(BaseModel):
    module_name: str
    component: Type[BaseComponent]
    profile: ComponentProfile
    interfaces: Dict[str, InterfaceInfo]


class ComponentRegister:
    components: Dict[str, ComponentInfo] = {}

    @classmethod
    def register(cls, module_name):
        try:
            profile = ComponentProfile.load_by_module_name(module_name)
            component = profile.load_enter_class()
            interfaces = {i.interface: InterfaceRegister.interfaces[i.interface] for i in profile.implements}
            component_info = ComponentInfo(module_name=module_name, component=component, profile=profile,
                                           interfaces=interfaces)
            cls.components[module_name] = component_info
            logger.info(f"Load Component [{module_name}] Success")
        except Exception as ex:
            logger.warning(f"Load Component [{module_name}] Error: {ex}")

    @classmethod
    def get_components(cls):
        return cls.components
