import json
import os
from socket import timeout
import sys
import time
import urllib.error
import urllib.parse
import uuid
from datetime import timedelta
import asyncio

import httpx
import websockets
import typer  # CLI工具支持
from rich import print as pprint
from rich.progress import BarColumn, Column, Progress, Table, TimeElapsedColumn
from utils.http_client import HttpClient

from services.websocket_service import send_to_websocket


async def check_comfy_server_running(base_url):  # 检查ComfyUI是否运行
    async with HttpClient.create(timeout=10) as client:
        url = f"{base_url}/api/prompt"
        response = await client.get(url)
        return response.status_code == 200


async def execute(
    workflow: dict,  # 可指定的api工作流 JSON
    base_url,  # ComfyUI服务地址
    wait=True,  # 是否等待执行完成
    verbose=False,  # 是否打印详细信息
    local_paths=False,
    timeout=300,  # 超时时间
    ctx: dict = {},  # 上下文信息
):
    if not await check_comfy_server_running(base_url):
        pprint(
            f"[bold red]ComfyUI not running on specified address ({base_url})[/bold red]"
        )
        raise typer.Exit(code=1)

    progress = None
    start = time.time()
    if wait:
        pprint("Executing comfyui workflow")
        progress = ExecutionProgress()
        # Remove or comment out the line below to avoid starting the live display
        # progress.start()
    else:
        print("Queuing comfyui workflow")

    execution = WorkflowExecution(
        workflow, base_url, verbose, progress, local_paths, timeout, ctx=ctx
    )  # 创建WorkflowExecution实例

    try:
        if wait:
            await execution.connect()  # 与ComfyUI服务建立websocket连接
        await execution.queue()  # 将工作流提交到ComfyUI服务
        if wait:
            await execution.watch_execution()  # 监听工作流执行状态
            end = time.time()
            progress.stop()  # 停止进度条
            progress = None  # 清空进度条

            if len(execution.outputs) > 0:
                pprint("[bold green]\nOutputs:[/bold green]")

                for f in execution.outputs:  # 打印输出结果
                    pprint(f)

            elapsed = timedelta(seconds=end - start)  # 计算执行时间
            pprint(
                f"[bold green]\nWorkflow execution completed ({elapsed})[/bold green]"
            )
        else:
            pprint("[bold green]Workflow queued[/bold green]")
    finally:
        if progress:
            progress.stop()
    return execution


class ExecutionProgress(Progress):
    def get_renderables(self):  # 自定义渲染逻辑
        table_columns = (
            (
                Column(no_wrap=True)
                if isinstance(_column, str)
                else _column.get_table_column().copy()
            )
            for _column in self.columns
        )  # 创建表格列

        for task in self.tasks:  # 遍历任务
            percent = "[progress.percentage]{task.percentage:>3.0f}%".format(
                task=task
            )  # 计算任务进度
            if task.fields.get("progress_type") == "overall":  # 如果任务类型为总体进度
                overall_table = Table.grid(
                    *table_columns, padding=(0, 1), expand=self.expand
                )
                overall_table.add_row(
                    BarColumn().render(task), percent, TimeElapsedColumn().render(task)
                )
                yield overall_table
            else:  # 如果任务类型为节点进度
                yield self.make_tasks_table([task])


class WorkflowExecution:
    def __init__(
        self,
        workflow,
        base_url,
        verbose,
        progress,
        local_paths,
        timeout=30,
        ctx: dict = {},
    ):
        self.workflow = workflow
        self.base_url = base_url
        self.verbose = verbose
        self.local_paths = local_paths
        self.client_id = str(uuid.uuid4())  # 生成客户端ID
        self.outputs = []  # 存储输出结果
        self.progress = progress  # 进度条
        self.remaining_nodes = set(
            self.workflow.keys()
        )  # 初始化待执行节点，此时待执行节点为工作流中的所有节点
        self.total_nodes = len(self.remaining_nodes)  # 总节点数
        if progress:  # 如果进度条存在，则添加总体进度任务
            self.overall_task = self.progress.add_task(
                "", total=self.total_nodes, progress_type="overall"
            )
        self.current_node = None  # 当前执行节点
        self.progress_task = None  # 内部有迭代进度的节点进度条任务
        self.progress_node = None  # 内部有迭代进度的节点
        self.prompt_id = None  # 任务下发后ComfyUI返回的ID
        self.ws = None  # WebSocket连接
        self.timeout = timeout  # 超时时间
        self.ctx = ctx  # 上下文信息

    async def connect(self):
        if self.base_url.startswith("https"):
            self.ws_core = "wss://"
        else:
            self.ws_core = "ws://"
        ws_url = self.base_url.split("//")[1]
        if "/" in ws_url:
            ws_url = ws_url.split("/")[0]
        self.ws = await websockets.connect(
            f"{self.ws_core}{ws_url}/ws?clientId={self.client_id}"
        )  # 建立WebSocket连接

    async def queue(self):
        data = {"prompt": self.workflow, "client_id": self.client_id}
        async with HttpClient.create() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/prompt", json=data
                )  # 下发任务
                body = response.json()  # 获取响应体
                self.prompt_id = body["prompt_id"]  # 获取任务ID
            except httpx.HTTPStatusError as e:
                message = "An unknown error occurred"
                if e.response.status_code == 500:
                    message = e.response.text
                elif e.response.status_code == 400:
                    body = e.response.json()
                    if body["node_errors"].keys():
                        message = json.dumps(body["node_errors"], indent=2)

                self.progress.stop()  # 停止进度条

                pprint(
                    f"[bold red]Error running workflow\n{message}[/bold red]"
                )  # 打印错误信息
                await send_to_websocket(
                    self.ctx.get("session_id"),
                    {"type": "error", "error": message},  # 发送错误信息到WebSocket
                )
                raise Exception(message)  # 抛出异常

    async def watch_execution(self):
        async for message in self.ws:  # 监听工作流执行状态
            if isinstance(message, str):
                message = json.loads(message)
                if message.get("data", {}).get("prompt_id") != self.prompt_id:
                    continue  # 如果任务ID不匹配，则跳过
                if not await self.on_message(message):
                    # get task_id and check if task_id is saved to prompt
                    async with HttpClient.create() as client:
                        try:
                            response = await client.get(
                                f"{self.base_url}/history/{self.prompt_id}"
                            )
                            if response.status_code != 200:
                                raise Exception(response)  # 抛出异常
                            response_body = response.json()
                            if self.prompt_id in response_body:
                                break  # 如果任务ID在响应体中，表示任务已处理结束，结束监听
                            else:
                                continue  # 如果任务ID不在响应体中，则跳过
                        except Exception as e:
                            pprint(
                                f"[bold red]Error getting history\n{str(e)}[/bold red]"
                            )
                            raise Exception(message)

    def update_overall_progress(self):
        self.progress.update(
            self.overall_task, completed=self.total_nodes - len(self.remaining_nodes)
        )

    def get_node_title(self, node_id):  # 获取节点标题
        node = self.workflow[node_id]
        if "_meta" in node and "title" in node["_meta"]:
            return node["_meta"]["title"]
        return node["class_type"]

    def log_node(self, type, node_id):
        if not self.verbose:
            return

        node = self.workflow[node_id]
        class_type = node["class_type"]
        title = self.get_node_title(node_id)

        if title != class_type:
            title += f"[bright_black] - {class_type}[/]"
        title += f"[bright_black] ({node_id})[/]"

        pprint(f"{type} : {title}")

    def format_image_path(self, img):
        query = urllib.parse.urlencode(img)
        return f"{self.base_url}/view?{query}"  # 查询对应图片的请求地址，用于在浏览器中查看图片

    async def on_message(self, message):  # 消息处理路由
        data = message["data"] if "data" in message else {}
        if "prompt_id" not in data or data["prompt_id"] != self.prompt_id:
            return True

        if message["type"] == "status":  # 任务正在等待
            return await self.on_status(data)
        elif message["type"] == "executing":  # 任务正在执行
            return await self.on_executing(data)
        elif (
            message["type"] == "execution_cached"
        ):  # 记录当前工作流从前一次工作流继承可复用的节点信息
            await self.on_cached(data)
        elif message["type"] == "progress":  # 迭代类节点内部执行进度，如采样节点
            await self.on_progress(data)
        elif message["type"] == "executed":  # 任务已执行
            await self.on_executed(data)
        elif message["type"] == "execution_error":  # 任务执行错误
            await self.on_error(data)

        return True

    async def on_status(self, data):  # 任务正在等待
        queue = data['data']['status']['exec_info']['queue_remaining']
        await send_to_websocket(
            self.ctx.get("session_id"),
            {
                "type": "tool_call_progress",
                "tool_call_id": self.ctx.get("tool_call_id"),
                "session_id": self.ctx.get("session_id"),
                "update": f"In queue, there's {queue} works ahead...",
            },
        )

    async def on_executing(self, data):
        if self.progress_task:
            self.progress.remove_task(self.progress_task)  # 移除进度条任务
            self.progress_task = None

        if data["node"] is None:
            return (
                False  # 如果状态为executing，并且data["node"]为None，表示工作流执行结束
            )
        else:
            if self.current_node:
                self.remaining_nodes.discard(self.current_node)
                self.update_overall_progress()  # 更新总体进度
            # Use display_node if available, otherwise use node
            node_id = data.get("display_node", data.get('node'))

            self.current_node = node_id  # 获取当前节点
            self.log_node("Executing", node_id)
            if self.ctx.get("session_id"):
                await send_to_websocket(
                    self.ctx.get("session_id"),
                    {
                        "type": "tool_call_progress",
                        "tool_call_id": self.ctx.get("tool_call_id"),
                        "session_id": self.ctx.get("session_id"),
                        "update": f"Executing {self.get_node_title(node_id)}",
                    },
                )
        return True

    async def on_cached(self, data):
        nodes = data["nodes"]
        for n in nodes:
            self.remaining_nodes.discard(n)  # 从待执行节点中移除已缓存的节点
            self.log_node("Cached", n)
        self.update_overall_progress()  # 更新总体进度

    async def on_progress(self, data):
        node = data["node"]
        if self.ctx.get("session_id"):
            await send_to_websocket(
                self.ctx.get("session_id"),
                {
                    "type": "tool_call_progress",
                    "tool_call_id": self.ctx.get("tool_call_id"),
                    "session_id": self.ctx.get("session_id"),
                    "update": f"Executing {self.get_node_title(node)} {round(data['value'] / data['max'] * 100)}%",
                },
            )
        if self.progress_node != node:
            self.progress_node = node
            if self.progress_task:
                self.progress.remove_task(self.progress_task)

            self.progress_task = self.progress.add_task(
                self.get_node_title(node), total=data["max"], progress_type="node"
            )

        self.progress.update(self.progress_task, completed=data["value"])

    async def on_executed(self, data):
        self.remaining_nodes.discard(data["node"])
        self.update_overall_progress()

        if "output" not in data:
            return

        output = data["output"]

        if output is None:
            return

        for img in output.get("images", []):
            self.outputs.append(self.format_image_path(img))  # 记录图片输出

        for gif in output.get("gifs", []):
            self.outputs.append(self.format_image_path(gif))  # 记录gifs输出

        await send_to_websocket(
            self.ctx.get("session_id"),
            {
                "type": "tool_call_progress",
                "tool_call_id": self.ctx.get("tool_call_id"),
                "session_id": self.ctx.get("session_id"),
                "update": "",  # clear the progress update section by send empty string
            },
        )

    async def on_error(self, data):
        pprint(
            f"[bold red]Error running workflow\n{json.dumps(data, indent=2)}[/bold red]"
        )
        await send_to_websocket(
            self.ctx.get("session_id"),
            {"type": "error", "error": json.dumps(data, indent=2)},
        )
        raise Exception(json.dumps(data, indent=2))


async def upload_image(
    image, base_url, filename=None, subfolder='jaaz'
):  # 图片上传到ComfyUI指定的路径下
    # Create a tuple with (filename, file_content) for proper multipart upload
    files = {"image": (filename, image)}
    data = {"type": "input", "subfolder": subfolder, "overwrite": "false"}
    async with HttpClient.create() as client:
        try:
            response = await client.post(
                f"{base_url}/upload/image", files=files, data=data
            )
            body = response.json()
            image_name = body["name"]
            return f"{subfolder}/{image_name}"
        except httpx.HTTPStatusError as e:
            message = "An unknown error occurred"
            if e.response.status_code == 500:
                message = e.response.text
            elif e.response.status_code == 400:
                body = e.response.json()
                if body["node_errors"].keys():
                    message = json.dumps(body["node_errors"], indent=2)
            pprint(f"[bold red]Error uploading image\n{message}[/bold red]")
            raise Exception(message)
