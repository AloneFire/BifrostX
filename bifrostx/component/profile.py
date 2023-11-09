from bifrostx.core.profile import BaseProfile
from typing import List
from bifrostx.adapter.profile import ImplementInterface, InterfaceProfile
from pydantic import model_validator


class ComponentProfile(BaseProfile):
    references: List[ImplementInterface] = []
    enter_class: str = "Component"

    @classmethod
    def load_by_module_name(cls, model_name):
        return super().load_by_module_name(f"Components.{model_name}")

    @model_validator(mode="after")
    def validate_interface(self):
        for reference in self.references:
            try:
                interface_info = InterfaceProfile.load_by_module_name(
                    reference.interface
                )
            except ImportError:
                raise ValueError(
                    f"Component[{self.display_name}]所依赖的Interface[{reference.interface}]不存在"
                )
            if interface_info.version == reference.interface_version:
                return self
            raise ValueError(
                f"Component[{self.display_name}]所依赖的Interface[{reference.interface}]版本不一致"
            )
