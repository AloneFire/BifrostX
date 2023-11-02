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
    module_name: str = ""
    version: str
    display_name: str
    bifrost_version: str
    dependencies: List[str] = []
    enter_class: str

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
    def load_by_module(cls, module):
        file = Path(module.__file__).parent.joinpath('bifrost.toml')
        if not file.exists():
            raise ValueError("未找到bifrost.toml")
        info = tomli.loads(file.read_text(encoding='utf-8'))
        rel = cls(**info)
        rel.module_name = module.__name__
        return rel

    @classmethod
    def load_by_module_name(cls, module_name):
        module = import_module(module_name)
        return cls.load_by_module(module)

    def load_enter_class(self):
        enter_class_path = self.enter_class.strip().strip(".").rsplit(":", 1)
        if len(enter_class_path) == 1:
            module = import_module(self.module_name)
        else:
            module = import_module(f"{self.module_name}.{enter_class_path[0]}")
        if hasattr(module, enter_class_path[-1]):
            return getattr(module, enter_class_path[-1])
        else:
            raise ValueError(f"Enter Class: {self.module_name}.{self.enter_class}不存在")

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
