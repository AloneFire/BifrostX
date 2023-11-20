from bifrostx.core.profile import BaseProfile
from bifrostx.interface.profile import InterfaceProfile
from pydantic import model_validator


class ComponentProfile(BaseProfile):
    enter_class: str = "Component"
    _module_prefix: str = "Components"
