from pydantic import BaseModel, field_validator, validate_call
from pathlib import Path
from config import Config
import sys
from bifrost.utils.logger import logger
from bifrost.interface.profile import InterfaceProfile
from bifrost.adapter.profile import AdapterProfile
from bifrost.component.profile import ComponentProfile


class StartConfigSchema(BaseModel):
    extension_dir: str

    @classmethod
    @field_validator("extension_dir")
    def validate_extension_dir(cls, value: str):
        path = Path(value)
        if path.exists():
            return value
        raise ValueError(f"extension_dir {path.absolute()} doesn't exist")


def init_extension_dir(extension_dir):
    """
    初始化扩展目录
    """
    ext_dir = Path(extension_dir)
    if str(ext_dir.absolute()) not in sys.path:
        sys.path.append(str(ext_dir.absolute()))
    Config.EXTENSION_DIR = str(ext_dir.absolute())
    init_dirs = {
        "Interfaces": InterfaceProfile,
        "Adapters": AdapterProfile,
        "Components": ComponentProfile
    }
    for init_dir, profile_validator in init_dirs.items():
        item_dir = ext_dir.joinpath(init_dir)
        item_dir.mkdir(parents=True, exist_ok=True)
        item_dir.joinpath("__init__.py").touch(exist_ok=True)
        for item in item_dir.iterdir():
            if item.is_dir() and item.name not in ("__pycache__",):
                profile = profile_validator.load_by_model_name(item.name)
                logger.info(f"Load {init_dir}.{item.name}: {profile}")


@validate_call
def start(config: StartConfigSchema):
    init_extension_dir(config.extension_dir)


if __name__ == "__main__":
    start(config={"extension_dir": "."})
    logger.info("start")
