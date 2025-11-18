from typing import Optional, TypedDict
from langchain_core.tools import BaseTool


class ToolInfoRequired(TypedDict):  # 工具信息必需字段
    tool_function: BaseTool
    provider: str


class ToolInfoOptional(TypedDict, total=False):  # 工具信息可选字段
    display_name: Optional[str]
    type: Optional[str]


class ToolInfo(ToolInfoRequired, ToolInfoOptional):  # 工具信息
    pass


class ToolInfoJsonRequired(TypedDict):  # 工具信息JSON必需字段
    provider: str
    id: str


class ToolInfoJson(ToolInfoJsonRequired, ToolInfoOptional):  # 工具信息JSON
    pass
