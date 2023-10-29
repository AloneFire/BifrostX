from pydantic import BaseModel, field_validator, validate_call
from pathlib import Path
import os
import sys


class StartConfigSchema(BaseModel):
    extension_dir: str

    @field_validator("extension_dir")
    @classmethod
    def validate_extension_dir(cls, value: str):
        path = Path(value)
        if path.exists():
            return value
        raise ValueError(f"extension_dir {path.absolute()} doesn't exist")


def init_extension_dir(config: StartConfigSchema):
    ext_dir = Path(config.extension_dir)
    interfaces_dir = ext_dir.joinpath("Interfaces")
    adapters_dir = ext_dir.joinpath("Adapters")
    components_dir = ext_dir.joinpath("Components")
    os.makedirs(interfaces_dir, exist_ok=True)
    os.makedirs(adapters_dir, exist_ok=True)
    os.makedirs(components_dir, exist_ok=True)


def load_extensions(config: StartConfigSchema):
    print(sys.path)
    ext_dir = Path(config.extension_dir)


@validate_call
def start(config: StartConfigSchema):
    init_extension_dir(config)
    load_extensions(config)


if __name__ == "__main__":
    start(config={"extension_dir": "extensions"})
