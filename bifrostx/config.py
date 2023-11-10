from typing import Any, Tuple, Type, Dict, Union

import tomli
from pathlib import Path

from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class TomlConfigSettingSource(PydanticBaseSettingsSource):
    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> tuple[Any, str, bool]:
        config_file = self.config.get("bifrostx_config", "config.toml")
        file_path = Path(config_file)
        if file_path.exists():
            data = tomli.loads(file_path.read_text("utf8"))
            field_value = data.get(field_name)
            return field_value, field_name, False
        else:
            file_path.touch()
            return None, field_name, False

    def prepare_field_value(
        self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
    ) -> Any:
        return value

    def __call__(self, *args, **kwargs):
        d = {}
        for field_name, field in self.settings_cls.model_fields.items():
            field_value, field_key, value_is_complex = self.get_field_value(
                field, field_name
            )
            field_value = self.prepare_field_value(
                field_name, field, field_value, value_is_complex
            )
            if field_value is not None:
                d[field_key] = field_value

        return d


class ConfigObject(BaseSettings):
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (init_settings, TomlConfigSettingSource(settings_cls))

    def get_extension_config(self, module: Union[str, Type], instances=False) -> Dict:
        key = "instances" if instances else "config"
        module_name = module
        if not isinstance(module, str):
            module_name = module.__name__
        modules = module_name.split(".")[:2]
        if len(modules) == 2 and hasattr(self, modules[0]):
            return getattr(self, modules[0]).get(modules[1], {}).get(key, {})
        raise ValueError(f"未找到相关{module_name}配置")

    LOG_LEVEL: str = "DEBUG"
    EXTENSION_DIR: str = "."
    FONTEND_DIR: str = "fontend"
    Adapters: Dict = {}
    Interfaces: Dict = {}
    Components: Dict = {}


Config = ConfigObject()
