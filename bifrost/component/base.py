from pydantic import BaseModel


class BaseComponent:
    instance_config_schema: BaseModel = None

    def __init__(self, instance_config):
        self.instance_config = (
            self.instance_config_schema(**instance_config)
            if self.instance_config_schema
            else None
        )
