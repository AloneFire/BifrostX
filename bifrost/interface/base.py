from abc import ABC


class BaseInterface(ABC):
    def __init__(self, config):
        self.config = config
