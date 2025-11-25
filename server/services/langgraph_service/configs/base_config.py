from typing import Annotated, Optional, Dict, Any, Sequence, List, TypedDict
from langgraph.types import Command
from langgraph.prebuilt import InjectedState
from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool, InjectedToolCallId, tool  # type: ignore
from langgraph_swarm.handoff import METADATA_KEY_HANDOFF_DESTINATION
from models.tool_model import ToolInfoJson


class ToolConfig(TypedDict):
    """工具配置"""

    tool: str


def _normalize_agent_name(name: str) -> str:  # 将agent名称转换为工具名称的格式
    """Normalize agent name to be compatible with tool names."""
    return name.lower().replace(" ", "_").replace("-", "_")


def create_handoff_tool(
    *,
    agent_name: str,
    name: Optional[str] = None,
    description: Optional[str] = None,  # *号要求其后面的参数必须以关键字参数的形式传入
) -> BaseTool:  # 创建一个工具，可以切换到指定的agent
    """Create a tool that can handoff control to the requested agent.

    Args:
        agent_name: The name of the agent to handoff control to, i.e.
            the name of the agent node in the multi-agent graph.
            Agent names should be simple, clear and unique, preferably in snake_case,
            although you are only limited to the names accepted by LangGraph
            nodes as well as the tool names accepted by LLM providers
            (the tool name will look like this: `transfer_to_<agent_name>`).
        name: Optional name of the tool to use for the handoff.
            If not provided, the tool name will be `transfer_to_<agent_name>`.
        description: Optional description for the handoff tool.
            If not provided, the tool description will be `Ask agent <agent_name> for help`.
    """
    if name is None:
        name = f"transfer_to_{_normalize_agent_name(agent_name)}"

    if description is None:
        description = f"Ask agent '{agent_name}' for help"

    @tool(
        name,
        description=description
        + """
    \nIMPORTANT RULES:
            1. You MUST complete the other tool calls and wait for their result BEFORE attempting to transfer to another agent
            2. Do NOT call this handoff tool with other tools simultaneously
            3. Always wait for the result of other tool calls before making this handoff call
    """,
    )
    def handoff_to_agent(
        state: Annotated[
            Dict[str, Any], InjectedState
        ],  # 自动注入当前图的状态，包括消息历史等
        tool_call_id: Annotated[str, InjectedToolCallId],  # 自动注入工具调用ID
    ) -> Command[Any]:
        tool_message = ToolMessage(
            content=f"<hide_in_user_ui> Successfully transferred to {agent_name}",
            name=name,
            tool_call_id=tool_call_id,
        )  # 创建记录切换操作的ToolMessage
        return Command(
            goto=agent_name,  # 切换到指定的agent，即告诉graph应该跳转到哪个节点
            graph=Command.PARENT,  # 切换到父图，即在哪个图层级执行跳转
            update={
                "messages": state["messages"] + [tool_message],
                "active_agent": agent_name,
            },  # 更新状态，包括消息历史和当前激活的agent
        )

    setattr(
        handoff_to_agent, 'metadata', {METADATA_KEY_HANDOFF_DESTINATION: agent_name}
    )  # 设置工具的元数据，用于记录切换的目的地

    return handoff_to_agent  # 返回创建好的工具函数


class HandoffConfig(TypedDict):
    """切换智能体配置"""

    agent_name: str
    description: str


class BaseAgentConfig:
    """智能体配置基类

    此类用于存储智能体配置信息的配置类，不是实际的智能体。
    实际的智能体将通过 LangGraph 的 create_react_agent 函数创建。
    """

    def __init__(
        self,
        name: str,
        tools: Sequence[ToolInfoJson],
        system_prompt: str,
        handoffs: Optional[List[HandoffConfig]] = None,
    ) -> None:
        self.name = name
        self.tools = tools
        self.system_prompt = system_prompt
        self.handoffs: List[HandoffConfig] = handoffs or []
