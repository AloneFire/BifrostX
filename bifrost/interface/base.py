from abc import ABC
from bifrost.config import Config


class BaseInterface(ABC):
    def __init__(self, instance_config):
        self.instance_config = instance_config
