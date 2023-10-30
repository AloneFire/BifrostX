from bifrost.core.profile import BaseProfile


class InterfaceProfile(BaseProfile):
    @classmethod
    def load_by_model_name(cls, model_name):
        return super().load_by_model_name(f"Interfaces.{model_name}")
