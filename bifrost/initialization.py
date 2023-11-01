from pathlib import Path
import sys
from bifrost.interface.profile import InterfaceProfile
from bifrost.adapter.profile import AdapterProfile
from bifrost.component.profile import ComponentProfile
from bifrost.config import Config
from bifrost.utils.logger import logger


def init_extension_dir():
    """
    初始化扩展目录
    """
    ext_dir = Path(Config.EXTENSION_DIR)
    if str(ext_dir.absolute()) not in sys.path:
        sys.path.append(str(ext_dir.absolute()))
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
