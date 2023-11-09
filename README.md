![Python Version](https://img.shields.io/badge/python-%3E%3D3.9-green)
# BifrostX
> 插件式快速服务框架

## 安装
```
pip install bifrostx
```

## 快速开始
```
bifrostx server
```

## 开发指南
所有拓展必须在对应的目录下，且必须有`__init__.py`文件与`bifrostx.toml`文件

### Interface
定义功能接口，解耦组件与适配器，应用与实现分离。   
`bifrostx.toml`参数定义如下：
```toml
version="0.1.0" # 版本号
bifrostx_version="0.1.0" # 最低兼容bifrostx版本号，可选
display_name="大语言模型对话接口" # 接口描述名称
enter_class = "interface:Interface" # 入口类，必须继承 bifrostx.interface.BaseInterface, 可选默认为模块下 Interface类
```
#### Demo
```python
from bifrostx.interface.base import BaseInterface
from abc import abstractmethod
# 定义接口
class Interface(BaseInterface):
    @abstractmethod
    def chat(
        self,
        prompt: List[ChatHistory],
        temperature: Optional[confloat(gt=0, lt=1)] = None,
        top_p: Optional[confloat(gt=0, lt=1)] = None,
    ) -> ChatHistory:
        return NotImplemented
```

### Adapter
适配器，实现Interface接口功能。   
`bifrostx.toml`参数定义如下：
```toml
version = "0.1.0"  # 版本号
bifrostx_version = "0.1.0" # 最低兼容bifrostx版本号，可选
display_name = "OpenAI-GPT" # 适配器描述名称
dependencies = ["openai", "tiktoken"] # 依赖的pypi包，可选
enter_class = "adapter:Adapter" # 入口类，必须继承要实现的 Interface接口，可选默认为模块下 Adapter类
[[implements]] # 实现的接口列表
interface = "llm_chat" # 实现接口名称
interface_version = "0.1.0" # 实现接口版本号
```
#### Demo
```python
from bifrostx.config import Config
from bifrostx.utils.logger import logger
from bifrostx.core.data_model import BaseModel, validate_call, confloat
from Interfaces.llm_chat.interface import Interface

# 配置类
class AdapterInstanceConfig(BaseModel):
    gpt_model: OpenaiModel = OpenaiModel.GPT35
    api_base: str = "https://api.openai.com/v1"
    api_type: OpenaiApiType = OpenaiApiType.OPENAI
    api_key: str
    default_temperature: confloat(gt=0, lt=1) = 0.2

# 适配器
class Adapter(Interface):
    # 注册适配器实例配置
    instance_config_schema = AdapterInstanceConfig
    def __init__(self, instance_config: AdapterInstanceConfig):
        super().__init__(instance_config)
        # 从 config.toml 中获取配置
        self.config = Config.get_extension_config(__name__)

    # 参数验证装饰器
    @validate_call
    # 实现接口方法
    def chat(
        self,
        prompt: List[ChatHistory],
        temperature: Optional[confloat(gt=0, lt=1)] = None,
        top_p: Optional[confloat(gt=0, lt=1)] = None,
    ):
        inputs = ChatInputs(prompt=prompt, temperature=temperature, top_p=top_p)
        resp = self._chat(inputs, use_stream=False)
        return ChatHistory(**resp["choices"][0]["message"])
```


### Component
组件，组合功能实现应用 api。服务接口默认都在`/api`路由下
`bifrostx.toml`参数定义如下：
```toml
display_name = "对话" # 组件描述名称
version = "0.1.0" # 版本号
bifrostx_version = "0.1.0" # 最低兼容bifrostx版本号，可选
enter_class = "component:Component" # 入口类，必须继承 bifrostx.component.BaseComponent, 可选默认为模块下 Component类
[[references]] # 引用的接口列表
interface = "llm_chat" # 引用接口名称
interface_version = "0.1.0" # 引用接口版本号
```
组件api定义必须以方法开头`api_`，api 请求参数与返回值，只能为json 可转换格式。

#### Demo
```python
from bifrostx.component.base import BaseComponent
from Interfaces.llm_chat.interface import Interface as LLL_Chat_Interface
from bifrostx.core.data_model import BaseModel

# 组件实例配置类
class ComponentConfig(BaseModel):
    llm_chat_instance: str

# api请求参数类
class ApiChatCompletionsInputs(BaseModel):
    messages: List[ChatHistory]

# 组件
class Component(BaseComponent):
    # 注册组件实例配置类
    instance_config_schema = ComponentConfig

    @property
    def llm_chat_instance(self):
        # 获取接口实现实例
        instance = LLL_Chat_Interface.get_instance(
            self.instance_config.llm_chat_instance
        )
        if instance is None:
            raise Exception("LLM Chat instance not found")
        return instance
    # api接口chat_completions
    def api_chat_completions(self, inputs: ApiChatCompletionsInputs):
        # 调用接口方法
        output = self.llm_chat_instance.chat(prompt=inputs.messages)
        return output
```

### Fontend
前端目录，静态资源目录默认为`fontend`, 默认访问首页为`index.html`
> `/api`、`/docs` 为保留路由, 同名目录不生效

## 配置

### `config.toml` 实例配置
```toml
LOG_LEVEL: str = "DEBUG" # 日志级别
EXTENSION_DIR: str = "./extensions" # 扩展目录
FONTEND_DIR: str = "frontend" # 前端目录
[Adapters.llm_openai_gpt.config] # 适配器配置 如：适配器为 llm_openai_gpt
proxy = "http://xxxx.xxxx.xxxx"
[Adapters.llm_openai_gpt.instances.gpt] # 适配器实例配置 如：适配器为 llm_openai_gpt 实例名称 gpt
api_key = "sk-xxxxxxxxxxx"
```

### `server.toml` 服务配置
```toml
app_name = "DemoServer" # 应用名称
server_bind = "0.0.0.0:18000" # 服务器绑定地址

[routers.chat_to_gpt] # 路由path 路由即为 /api/chat_to_gpt
component = "chat_with_llm" # 组件名称
summary = "聊天" # 路由描述
[routers.chat_to_gpt.config] # 组件配置
llm_chat_instance = "gpt"


[routers.chat_to_glm] # 路由配置
component = "chat_with_llm" # 组件名称
[routers.chat_to_glm.config] # 组件配置
llm_chat_instance = "glm"

```