from bifrostx.core.profile import BaseProfile


class InterfaceProfile(BaseProfile):
    enter_class: str = "Interface"

    @classmethod
    def load_by_module_name(cls, module_name):
        return super().load_by_module_name(f"Interfaces.{module_name}")
