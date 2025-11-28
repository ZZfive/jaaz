from pydantic import BaseModel


class ComfyWorkflow(BaseModel):
    id: int  # 工作流ID
    name: str  # 工作流名称
    description: str  # 工作流描述
    inputs: str  # 工作流输入
    outputs: str  # 工作流输出
