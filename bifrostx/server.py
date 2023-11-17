import tomli
import asyncio
from fastapi import FastAPI, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel, validate_call, field_validator
from hypercorn.config import Config as HypercornConfig
from hypercorn.asyncio import serve
from bifrostx.initialization import init_extension_dir
from typing import Dict, Optional
from bifrostx.component.register import ComponentRegister
from bifrostx.config import Config
from fastapi.middleware.cors import CORSMiddleware


class RouterConfig(BaseModel):
    path: str = ""
    component: str
    tags: list = []
    config: dict = {}

    @field_validator("path")
    def valiudate_path(cls, v):
        if not v.startswith("/"):
            raise ValueError("path必须以/开头")
        return v


class ServerConfig(BaseModel):
    app_name: str = "BifrostXServer"
    app_version: str = "0.1.0"
    app_description: str = ""
    server_bind: str = "127.0.0.1:8100"
    server_workers: int = 2
    server_access_log: str = "-"
    server_error_log: str = "-"
    server_use_reloader: bool = True
    server_cors_allow_origins: list = []
    routers: Dict[str, RouterConfig] = {}


def register_routers(app: FastAPI, server_config: ServerConfig):
    api_router = APIRouter(prefix="/api")
    for router_name, router_config in server_config.routers.items():
        if router_config.component not in ComponentRegister.components:
            raise ValueError(f"未找到Component: {router_config.component}")
        component_info = ComponentRegister.components[router_config.component]
        component_instance_config = router_config.config
        component = component_info.component(component_instance_config)
        endpoints = [func for func in dir(component) if func.startswith("api_")]
        for endpoint in endpoints:
            path = router_config.path if router_config.path else f"/{router_name}"
            if not path.endswith("/"):
                path += "/"
            path += endpoint[4:]
            api_router.add_api_route(
                path=path,
                endpoint=getattr(component, endpoint),
                methods=["POST"],
                tags=router_config.tags,
            )
    app.include_router(api_router)
    if server_config.server_cors_allow_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=server_config.server_cors_allow_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


def create_app(server_config: ServerConfig):
    app = FastAPI(
        title=server_config.app_name,
        version=server_config.app_version,
        description=server_config.app_description,
    )
    # 注册routers
    register_routers(app, server_config)
    if Path(Config.FONTEND_DIR).exists():
        # 注册默认静态资源
        app.mount(
            "/",
            StaticFiles(directory=Config.FONTEND_DIR, html=True, check_dir=True),
            name="fontend",
        )
    return app


@validate_call
def start_server(server_config: ServerConfig = None):
    if server_config is None:
        config_file = Path("server.toml")
        if config_file.exists():
            server_config = tomli.loads(config_file.read_text("utf-8"))
            server_config = ServerConfig(**server_config)
        else:
            server_config = ServerConfig()
            config_file.touch()
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
