from bifrost.core.profile import BaseProfile
from pydantic import model_validator
from bifrost.interface.profile import InterfaceProfile


class AdapterProfile(BaseProfile):
    interface: str
    interface_version: str

    @classmethod
    def load_by_model_name(cls, model_name):
        return super().load_by_model_name(f"Adapters.{model_name}")

    @model_validator(mode='after')
    def validate_interface(self):
        try:
            interface_info = InterfaceProfile.load_by_model_name(self.interface)
        except ImportError:
            raise ValueError(f"Adapter[{self.name}]所依赖的Interface[{self.interface}]不存在")
        if interface_info.version == self.interface_version:
            return self
        raise ValueError(f"Adapter[{self.name}]所依赖的Interface[{self.interface}]版本不一致")
