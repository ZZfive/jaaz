import copy
import os
import traceback
import aiofiles
import toml
from typing import Dict, TypedDict, Literal, Optional

# 定义配置文件的类型结构


# 模型配置
class ModelConfig(
    TypedDict, total=False
):  # 继承至TypedDict可用于类型检查，total=False表示可选字段
    type: Literal["text", "image", "video"]  # 模型类型
    is_custom: Optional[bool]  # 是否自定义
    is_disabled: Optional[bool]  # 是否禁用


# 模型提供商配置
class ProviderConfig(TypedDict, total=False):
    url: str  # 提供商URL
    api_key: str  # 提供商API密钥
    max_tokens: int  # 最大令牌数
    models: Dict[str, ModelConfig]  # 模型列表
    is_custom: Optional[bool]  # 是否自定义


AppConfig = Dict[str, ProviderConfig]


DEFAULT_PROVIDERS_CONFIG: AppConfig = {  # 声明DEFAULT_PROVIDERS_CONFIG为AppConfig类型
    'jaaz': {
        'models': {
            # text models
            'gpt-4o': {'type': 'text'},
            'gpt-4o-mini': {'type': 'text'},
            'deepseek/deepseek-chat-v3-0324': {'type': 'text'},
            'anthropic/claude-sonnet-4': {'type': 'text'},
            'anthropic/claude-3.7-sonnet': {'type': 'text'},
        },
        'url': os.getenv('BASE_API_URL', 'https://jaaz.app').rstrip('/') + '/api/v1/',
        'api_key': '',
        'max_tokens': 8192,
    },
    'comfyui': {
        'models': {},
        'url': 'http://127.0.0.1:8188',
        'api_key': '',
    },
    'ollama': {
        'models': {},
        'url': 'http://localhost:11434',
        'api_key': '',
        'max_tokens': 8192,
    },
    'openai': {
        'models': {
            'gpt-4o': {'type': 'text'},
            'gpt-4o-mini': {'type': 'text'},
        },
        'url': 'https://api.openai.com/v1/',
        'api_key': '',
        'max_tokens': 8192,
    },
}

SERVER_DIR = os.path.dirname(os.path.dirname(__file__))  # 获取服务器目录
USER_DATA_DIR = os.getenv(
    "USER_DATA_DIR",
    os.path.join(SERVER_DIR, "user_data"),
)  # 获取用户数据目录
FILES_DIR = os.path.join(USER_DATA_DIR, "files")  # 获取用户文件目录


IMAGE_FORMATS = (
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",  # 基础格式
    ".bmp",
    ".tiff",
    ".tif",  # 其他常见格式
    ".webp",
)
VIDEO_FORMATS = (
    ".mp4",
    ".avi",
    ".mkv",
    ".mov",
    ".wmv",
    ".flv",
)


class ConfigService:
    def __init__(self):
        self.app_config: AppConfig = copy.deepcopy(
            DEFAULT_PROVIDERS_CONFIG
        )  # 深拷贝默认提供商配置
        self.config_file = os.getenv(
            "CONFIG_PATH", os.path.join(USER_DATA_DIR, "config.toml")
        )  # 获取用户配置文件路径
        self.initialized = False  # 初始化标志

    def _get_jaaz_url(self) -> str:
        """Get the correct jaaz URL"""
        return os.getenv('BASE_API_URL', 'https://jaaz.app').rstrip('/') + '/api/v1/'

    async def initialize(self) -> None:
        try:
            # Ensure the user_data directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

            # Check if config file exists
            if not self.exists_config():  # 检查配置文件是否存在
                print(
                    f"Config file not found at {self.config_file}, creating default configuration"
                )
                # Create default config file
                with open(self.config_file, "w") as f:  # 创建默认配置文件
                    toml.dump(self.app_config, f)
                print(f"Default config file created at {self.config_file}")
                self.initialized = True  # 初始化标志
                return

            async with aiofiles.open(self.config_file, "r") as f:  # 异步读取配置文件
                content = await f.read()
                config: AppConfig = toml.loads(content)  # 加载配置文件
            for provider, provider_config in config.items():
                if (
                    provider not in DEFAULT_PROVIDERS_CONFIG
                ):  # 检查提供商是否在默认提供商配置中
                    provider_config['is_custom'] = True  # 设置为自定义
                self.app_config[provider] = provider_config  # 添加提供商配置
                # image/video models are hardcoded in the default provider config 图片/视频模型在默认提供商配置中硬编码
                provider_models = DEFAULT_PROVIDERS_CONFIG.get(provider, {}).get(
                    'models', {}
                )  # 获取默认提供商配置的模型列表
                for model_name, model_config in provider_config.get(
                    'models', {}
                ).items():
                    # Only text model can be self added
                    if (
                        model_config.get('type') == 'text'
                        and model_name not in provider_models
                    ):
                        provider_models[model_name] = model_config
                        provider_models[model_name]['is_custom'] = True
                self.app_config[provider]['models'] = provider_models

            # 确保 jaaz URL 始终正确
            if 'jaaz' in self.app_config:
                self.app_config['jaaz']['url'] = self._get_jaaz_url()
        except Exception as e:
            print(f"Error loading config: {e}")
            traceback.print_exc()
        finally:
            self.initialized = True

    def get_config(self) -> AppConfig:
        if 'jaaz' in self.app_config:
            self.app_config['jaaz']['url'] = self._get_jaaz_url()
        return self.app_config

    async def update_config(self, data: AppConfig) -> Dict[str, str]:
        try:
            if 'jaaz' in data:
                data['jaaz']['url'] = self._get_jaaz_url()

            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, "w") as f:
                toml.dump(data, f)
            self.app_config = data

            return {
                "status": "success",
                "message": "Configuration updated successfully",
            }
        except Exception as e:
            traceback.print_exc()
            return {"status": "error", "message": str(e)}

    def exists_config(self) -> bool:
        return os.path.exists(self.config_file)  # 检查配置文件是否存在


config_service = ConfigService()
