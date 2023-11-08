# Bifrost

## 安装
```
pip install bifrost
```

## 快速开始
```
bifrost server
```

## 开发指南
所有拓展必须在对应的目录下，且必须有`__init__.py`文件与`bifrost.toml`文件

### Interface
定义功能接口，解耦组件与适配器，应用与实现分离。   
`bifrost.toml`参数定义如下：
```toml
version="0.1.0" # 版本号
bifrost_version="0.1.0" # 最低兼容bifrost版本号，可选
display_name="大语言模型对话接口" # 接口描述名称
enter_class = "interface:Interface" # 入口类，必须继承 bifrost.interface.BaseInterface, 可选默认为模块下 Interface类
```
### Adapter
适配器，实现Interface接口功能。   
`bifrost.toml`参数定义如下：
```toml
version = "0.1.0"  # 版本号
bifrost_version = "0.1.0" # 最低兼容bifrost版本号，可选
display_name = "OpenAI-GPT" # 适配器描述名称
dependencies = ["openai", "tiktoken"] # 依赖的pypi包，可选
enter_class = "adapter:Adapter" # 入口类，必须继承要实现的 Interface接口，可选默认为模块下 Adapter类
[[implements]] # 实现的接口列表
interface = "llm_chat" # 实现接口名称
interface_version = "0.1.0" # 实现接口版本号
```

### Component
组件，组合功能实现应用 api。服务接口默认都在`/api`路由下
`bifrost.toml`参数定义如下：
```toml
display_name = "对话" # 组件描述名称
version = "0.1.0" # 版本号
bifrost_version = "0.1.0" # 最低兼容bifrost版本号，可选
enter_class = "component:Component" # 入口类，必须继承 bifrost.component.BaseComponent, 可选默认为模块下 Component类
[[references]] # 引用的接口列表
interface = "llm_chat" # 引用接口名称
interface_version = "0.1.0" # 引用接口版本号
```
组件api定义必须以方法开头`api_`，api 请求参数与返回值，只能为json 可转换格式。

### fontend
前端目录服务`/`默认访问 `index.html`

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