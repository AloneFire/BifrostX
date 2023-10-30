from bifrost.core.profile import BaseProfile


class ComponentProfile(BaseProfile):
    @classmethod
    def load_by_model_name(cls, model_name):
        return super().load_by_model_name(f"Components.{model_name}")
