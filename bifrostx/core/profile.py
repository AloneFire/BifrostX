from pydantic import BaseModel, field_validator, model_validator
from bifrostx import __version__ as bifrostx_version
from distutils.version import LooseVersion
import re
from pathlib import Path
import tomli
from importlib import import_module
from typing import List
import pkg_resources
from bifrostx.utils.logger import logger
import sys
import subprocess
from bifrostx.config import Config


class InterfaceInfo(BaseModel):
    interface: str
    interface_version: str


class BaseProfile(BaseModel):
    _module_prefix: str = ""
    module_name: str = ""
    version: str
    display_name: str
    bifrostx_version: str = ""
    dependencies: List[str] = []
    enter_class: str
    references: List[InterfaceInfo] = []

    @field_validator("version")
    @classmethod
    def validate_version(cls, value: str):
        if re.match(r"^[0-9]+\.[0-9]+\.[0-9]+$", value):
            return value
        raise ValueError(f"版本号格式错误")

    @field_validator("bifrostx_version")
    @classmethod
    def validate_bifrostx_version(cls, value: str):
        if value:
            current_version = LooseVersion(bifrostx_version)
            if current_version >= LooseVersion(value):
                return value
            raise ValueError(f"拓展需求版本与当前不匹配")
        return value

    @classmethod
    def load_by_module(cls, module):
        file = Path(module.__file__).parent.joinpath("bifrostx.toml")
        if not file.exists():
            raise ValueError("未找到bifrostx.toml")
        info = tomli.loads(file.read_text(encoding="utf-8"))
        rel = cls(**info)
        rel.module_name = module.__name__
        return rel

    @classmethod
    def load_by_module_name(cls, module_name):
        return cls._load_by_module_name(module_name, prefix=cls._module_prefix.default)

    @classmethod
    def _load_by_module_name(cls, module_name, prefix=None):
        if prefix:
            module_name = f"{prefix}.{module_name}"
        file = (
            Path(Config.EXTENSION_DIR)
            .joinpath(*module_name.split("."))
            .joinpath("bifrostx.toml")
        )
        if not file.exists():
            raise ValueError("未找到bifrostx.toml")
        info = tomli.loads(file.read_text(encoding="utf-8"))
        rel = cls(**info)
        rel.module_name = module_name
        return rel

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

    @model_validator(mode="after")
    def validate_dependencies_and_interface(self):
        if self.dependencies:
            for dependency in self.dependencies:
                rel = re.search(
                    r"^([^>=<]*)([>=<]*)([^>=<]*)$", dependency.replace(" ", "")
                )
                if rel:
                    key, _, ver = rel.groups()
                    # TODO: 检查依赖版本冲突
                    if key not in [pkg.key for pkg in pkg_resources.working_set]:
                        subprocess.check_call(
                            [sys.executable, "-m", "pip", "install", dependency]
                        )
                else:
                    logger.warning(f"{self.display_name} 依赖包 {dependency} 格式不正确")

        if self.references:
            for reference in self.references:
                try:
                    reference_interface = self._load_by_module_name(
                        reference.interface, "Interfaces"
                    )
                except Exception:
                    raise ValueError(
                        f"{self._module_prefix}[{self.display_name}]所依赖的Interface[{reference.interface}]不存在"
                    )
                if reference_interface.version != reference.interface_version:
                    raise ValueError(
                        f"{self._module_prefix}[{self.display_name}]所依赖的Interface[{reference.interface}]版本不一致"
                    )
        return self
