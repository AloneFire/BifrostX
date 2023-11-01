from abc import ABC
from typing import Type


class BaseInterface(ABC):
    __bifrost_adapters__ = {}
    __bifrost_instances__ = {}

    def __init__(self, instance_config):
        self.instance_config = instance_config

    @classmethod
    def adapter_register(cls, adapter_class: "BaseInterface"):
        if isinstance(adapter_class, BaseInterface):
            cls.__bifrost_adapters__[adapter_class.__name__] = adapter_class
        else:
            raise ValueError(f"不支持此Adapter: {adapter_class.__name__}")

    @classmethod
    def get_adapters(cls):
        return list(cls.__bifrost_adapters__.values())

    @classmethod
    def instance_register(cls, instance_id: str, instance_config: dict):
        cls.__bifrost_instances__[instance_id] = instance_config

    @classmethod
    def get_instances(cls):
        data = {}
        if cls.__bifrost_instances__:
            data[cls.__name__] = cls.__bifrost_instances__
        for adapter_key, adapter in cls.__bifrost_adapters__.items():
            adapter_instances = adapter.get_instances().get(adapter_key)
            if adapter_instances:
                data[adapter_key] = adapter_instances
        return data
