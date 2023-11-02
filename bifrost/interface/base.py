from abc import ABC


class BaseInterface(ABC):
    def __init__(self, instance_config):
        self.instance_config = instance_config
