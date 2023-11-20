from bifrostx.core.profile import BaseProfile, InterfaceInfo
from pydantic import model_validator
from bifrostx.interface.profile import InterfaceProfile
from typing import List


class AdapterProfile(BaseProfile):
    implements: List[InterfaceInfo]
    enter_class: str = "Adapter"
    _module_prefix: str = "Adapters"

    @model_validator(mode="after")
    def validate_interface(self):
        for implement in self.implements:
            try:
                interface_info = InterfaceProfile.load_by_module_name(
                    implement.interface
                )
            except ImportError:
                raise ValueError(
                    f"Adapter[{self.display_name}]所依赖的Interface[{implement.interface}]不存在"
                )
            if interface_info.version == implement.interface_version:
                return self
            raise ValueError(
                f"Adapter[{self.display_name}]所依赖的Interface[{implement.interface}]版本不一致"
            )
