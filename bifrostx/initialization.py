from pathlib import Path
import sys
from bifrostx.interface.register import InterfaceRegister
from bifrostx.adapter.register import AdapterRegister
from bifrostx.component.register import ComponentRegister
from bifrostx.config import Config
from bifrostx.utils.logger import logger


def init_extension_dir():
    """
    初始化扩展目录
    """
    logger.info("Initializing extension directory...")
    ext_dir = Path(Config.EXTENSION_DIR)
    if str(ext_dir.absolute()) not in sys.path:
        sys.path.append(str(ext_dir.absolute()))
    init_dirs = {
        "Interfaces": InterfaceRegister,
        "Adapters": AdapterRegister,
        "Components": ComponentRegister,
    }
    for init_dir, register in init_dirs.items():
        item_dir = ext_dir.joinpath(init_dir)
        item_dir.mkdir(parents=True, exist_ok=True)
        item_dir.joinpath("__init__.py").touch(exist_ok=True)
        for item in item_dir.iterdir():
            if item.is_dir() and item.name not in ("__pycache__",):
                # 注册拓展
                register.register(item.name)
