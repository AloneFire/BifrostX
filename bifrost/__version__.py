from pathlib import Path
import tomli

metadata = tomli.loads(
    Path(__file__).parent.parent.joinpath("pyproject.toml").read_text()
)

name = metadata["project"]["name"]
version = metadata["project"]["version"]
