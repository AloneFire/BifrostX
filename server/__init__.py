from Components.chat_with_llm import Component, ComponentConfig
from Interfaces.llm_chat.interface import Interface as LLL_Chat_Interface
from bifrost.initialization import init_extension_dir
from fastapi import FastAPI, HTTPException, APIRouter, Request, Response
from fastapi.routing import APIRoute
from bifrost.utils.logger import logger
from bifrost.config import Config
from typing  import Callable

class OpenApiRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def open_route_handler(request: Request) -> Response:
            response: Response = await original_route_handler(request)
            return response

        return open_route_handler

open_router = APIRouter(
    prefix="/open", tags=["Open"], route_class=OpenApiRoute
)

init_extension_dir()
instacnce_congfig = ComponentConfig(llm_chat_instance = LLL_Chat_Interface.get_instance())
component = Component(instacnce_congfig)

# TODO：读取server config
endpoints = [func for func in dir(component) if func.startswith("api_")]
for endpoint in endpoints:
    open_router.add_api_route(
        path=f"/{component.__module__.split('.')[-1]}/{endpoint[4:]}",
        endpoint=getattr(component, endpoint),
        methods=["POST"],
    )