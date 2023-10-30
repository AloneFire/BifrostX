from pydantic import BaseModel, field_validator
from bifrost.__version__ import version
from distutils.version import LooseVersion
import re
from pathlib import Path
import tomli
from importlib import import_module


class BaseProfile(BaseModel):
    name: str
    version: str
    bifrost_version: str

    @classmethod
    @field_validator("name")
    def validate_name(cls, value: str):
        if re.match(r"^[a-zA-Z0-9_]+$", value):
            return value
        raise ValueError("name只能包含字母、数字和下划线")

    @classmethod
    @field_validator("bifrost_version")
    def validate_bifrost_version(cls, value: str):
        current_version = LooseVersion(version)
        if current_version >= LooseVersion(value):
            return value
        raise ValueError(f"拓展需求版本与当前不匹配")

    @classmethod
    def load_by_model(cls, model):
        info = Path(model.__file__).parent.joinpath('bifrost.toml').read_text(encoding='utf-8')
        info = tomli.loads(info)
        return cls(**info)

    @classmethod
    def load_by_model_name(cls, model_name):
        model = import_module(model_name)
        return cls.load_by_model(model)


