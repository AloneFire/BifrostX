import tomli
import asyncio
from fastapi import FastAPI, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel, validate_call
from hypercorn.config import Config as HypercornConfig
from hypercorn.asyncio import serve
from bifrost.initialization import init_extension_dir
from typing import List


class RouterConfig(BaseModel):
    path: str
    component: str
    adapter_instances: list = []


class ServerConfig(BaseModel):
    app_name: str = "BifrostServer"
    app_version: str = "0.1.0"
    app_description: str = ""
    server_bind: str = "0.0.0.0:8100"
    server_workers: int = 2
    server_access_log: str = "-"
    server_error_log: str = "-"
    server_use_reloader: bool = True
    routers: List[RouterConfig] = []


def index_view(server_config: ServerConfig):
    def index():
        fontend_index = "fontend/index.html"
        if Path(fontend_index).exists():
            return HTMLResponse(open(fontend_index).read())
        return HTMLResponse(f"<h1>Hello {server_config.app_name}</h1>")

    return index


def register_routers(app: FastAPI, server_config: ServerConfig):
    api_router = APIRouter(prefix="/api")
    # TODO: add routers
    from Components.chat_with_llm import Component, ComponentConfig
    from Interfaces.llm_chat.interface import Interface as LLL_Chat_Interface

    instacnce_congfig = ComponentConfig(
        llm_chat_instance=LLL_Chat_Interface.get_instance()
    )
    component = Component(instacnce_congfig)

    endpoints = [func for func in dir(component) if func.startswith("api_")]
    for endpoint in endpoints:
        api_router.add_api_route(
            path=f"/{component.__module__.split('.')[-1]}/{endpoint[4:]}",
            endpoint=getattr(component, endpoint),
            methods=["POST"],
        )
    app.include_router(api_router)


def create_app(server_config: ServerConfig):
    app = FastAPI(
        title=server_config.app_name,
        version=server_config.app_version,
        description=server_config.app_description,
    )
    # 注册首页
    app.add_api_route("/", index_view(server_config), methods=["GET"], summary="首页")
    # 注册routers
    register_routers(app, server_config)
    # 注册默认静态资源
    app.mount("/", StaticFiles(directory="fontend"), name="fontend")
    return app


@validate_call
def start_server(server_config: ServerConfig = None):
    if server_config is None:
        config_file = Path("server.toml")
        if config_file.exists():
            server_config = tomli.loads(config_file.read_text())
            server_config = ServerConfig(**server_config)
        else:
            server_config = ServerConfig()
    init_extension_dir()
    app = create_app(server_config)
    # [doc](https://hypercorn.readthedocs.io/en/latest/how_to_guides/configuring.html#)
    hypercorn_config = HypercornConfig()
    hypercorn_config.bind = (server_config.server_bind,)
    hypercorn_config.accesslog = server_config.server_access_log
    hypercorn_config.errorlog = server_config.server_error_log
    hypercorn_config.include_server_header = False
    hypercorn_config.use_reloader = server_config.server_use_reloader
    asyncio.run(serve(app, hypercorn_config))
