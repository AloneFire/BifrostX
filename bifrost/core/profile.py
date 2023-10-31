from pydantic import BaseModel, field_validator, model_validator
from bifrost.__version__ import version
from distutils.version import LooseVersion
import re
from pathlib import Path
import tomli
from importlib import import_module
from typing import List
import pkg_resources
from bifrost.utils.logger import logger
import sys
import subprocess


class BaseProfile(BaseModel):
    version: str
    display_name: str
    bifrost_version: str
    dependencies: List[str] = []

    @field_validator("version")
    @classmethod
    def validate_version(cls, value: str):
        if re.match(r"^[0-9]+\.[0-9]+\.[0-9]+$", value):
            return value
        raise ValueError(f"版本号格式错误")

    @field_validator("bifrost_version")
    @classmethod
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

    @model_validator(mode='after')
    def validate_dependencies(self):
        if not self.dependencies:
            return self
        for dependency in self.dependencies:
            rel = re.search(r"^([^>=<]*)([>=<]*)([^>=<]*)$", dependency.replace(" ", ""))
            if rel:
                key, _, ver = rel.groups()
                # TODO: 检查依赖版本冲突
                if key not in [pkg.key for pkg in pkg_resources.working_set]:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", dependency])
            else:
                logger.warning(f"{self.display_name} 依赖包 {dependency} 格式不正确")
        return self
