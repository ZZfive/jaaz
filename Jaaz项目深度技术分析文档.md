# Jaaz 项目深度技术分析文档

## 📋 目录
- [项目概述](#项目概述)
- [技术栈总览](#技术栈总览)
- [前端架构分析](#前端架构分析)
- [后端架构分析](#后端架构分析)
- [前后端交互机制](#前后端交互机制)
- [核心功能模块](#核心功能模块)
- [数据流与状态管理](#数据流与状态管理)
- [AI Agent 架构](#ai-agent-架构)
- [工具与模型集成](#工具与模型集成)
- [部署架构](#部署架构)
- [视觉类 Agent 项目建议](#视觉类-agent-项目建议)

---

## 项目概述

### 基本信息
- **项目名称**: Jaaz
- **定位**: 世界首个开源多模态画布创意代理（Open Source Canva AI Alternative）
- **核心功能**: AI 设计代理，支持图像/视频生成、无限画布、智能对话
- **架构模式**: Electron + React + Python FastAPI 混合桌面应用
- **版本**: v1.0.30

### 项目特点
1. **隐私优先**: 本地运行，支持 100% 离线或混合部署
2. **多模型支持**: 集成 GPT-4o、Midjourney、VEO3、Kling、Flux 等主流 AI 模型
3. **Agent 驱动**: 基于 LangGraph 的多智能体系统
4. **无限画布**: 支持视觉故事板和场景规划
5. **跨平台**: Windows、macOS、Linux 全平台支持

---

## 技术栈总览

### 前端技术栈
| 技术 | 版本 | 用途 |
|------|------|------|
| **React** | 19.1.0 | UI 框架 |
| **TypeScript** | 5.7.2 | 类型系统 |
| **Vite** | 6.2.0 | 构建工具 |
| **TanStack Router** | 1.120.15 | 路由管理 |
| **TanStack Query** | 5.80.3 | 数据获取与缓存 |
| **Zustand** | 5.0.5 | 轻量级状态管理 |
| **Socket.IO Client** | 4.8.1 | WebSocket 实时通信 |
| **Excalidraw** | 0.18.0 | 画布绘图引擎 |
| **tldraw** | 3.13.1 | 另一个画布方案 |
| **XYFlow** | 12.7.0 | 流程图/节点图 |
| **Tailwind CSS** | 4.0.17 | 样式框架 |
| **Radix UI** | - | 无障碍 UI 组件库 |
| **i18next** | 25.2.1 | 国际化 |
| **OpenAI SDK** | 4.98.0 | AI 模型调用 |

### 后端技术栈
| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | ≥3.12 | 后端语言（强制要求） |
| **FastAPI** | - | Web 框架 |
| **Uvicorn** | - | ASGI 服务器 |
| **Socket.IO** | 5.13.0 | WebSocket 服务 |
| **LangGraph** | 0.4.8 | Agent 编排框架 |
| **LangChain** | - | LLM 应用框架 |
| **OpenAI** | - | OpenAI API 客户端 |
| **Anthropic** | - | Claude API 客户端 |
| **Ollama** | - | 本地模型运行 |
| **aiosqlite** | - | 异步 SQLite 数据库 |
| **Pillow** | - | 图像处理 |
| **pymediainfo** | - | 媒体文件信息 |

### Electron 层
| 技术 | 版本 | 用途 |
|------|------|------|
| **Electron** | 35.1.0 | 桌面应用框架 |
| **electron-builder** | 24.0.0 | 打包工具 |
| **electron-updater** | 6.6.2 | 自动更新 |
| **Playwright** | 1.52.0 | 浏览器自动化 |
| **7zip-min** | 2.1.0 | 压缩解压 |

---

## 前端架构分析

### 1. 目录结构
```
react/
├── src/
│   ├── api/              # API 调用层
│   │   ├── auth.ts       # 认证 API
│   │   ├── chat.ts       # 聊天 API
│   │   ├── magic.ts      # 魔法生成 API
│   │   ├── canvas.ts     # 画布 API
│   │   ├── model.ts      # 模型配置
│   │   └── upload.ts     # 文件上传
│   ├── components/       # 组件库
│   │   ├── agent_studio/ # Agent 工作室
│   │   ├── canvas/       # 画布组件
│   │   ├── chat/         # 聊天组件
│   │   ├── settings/     # 设置面板
│   │   └── ui/           # 基础 UI 组件（Radix UI）
│   ├── contexts/         # React Context
│   │   ├── socket.tsx    # WebSocket 上下文
│   │   ├── configs.tsx   # 配置管理
│   │   └── AuthContext.tsx # 认证上下文
│   ├── stores/           # Zustand 状态管理
│   ├── routes/           # 路由页面
│   │   ├── index.tsx     # 首页
│   │   ├── canvas.$id.tsx # 画布页
│   │   ├── agent_studio.tsx # Agent 工作室
│   │   └── knowledge.tsx # 知识库
│   ├── hooks/            # 自定义 Hooks
│   ├── utils/            # 工具函数
│   ├── types/            # TypeScript 类型定义
│   └── i18n/             # 国际化配置
├── vite.config.ts
└── package.json
```

### 2. 核心架构设计

#### 2.1 路由架构（TanStack Router）
```typescript
// 基于文件系统的路由
routes/
  __root.tsx          → 根布局
  index.tsx           → 首页 (/)
  canvas.$id.tsx      → 画布页 (/canvas/:id)
  agent_studio.tsx    → Agent 工作室 (/agent_studio)
  knowledge.tsx       → 知识库 (/knowledge)
  assets.tsx          → 资产管理 (/assets)
```

**特点**：
- 自动代码分割（autoCodeSplitting）
- 类型安全的路由导航
- 支持搜索参数（如 sessionId）

#### 2.2 状态管理策略
项目采用多层次状态管理：

**1. React Context（全局共享）**
- `SocketContext`: WebSocket 连接状态
- `ConfigsContext`: 模型配置、工具选择
- `AuthContext`: 用户认证状态

**2. TanStack Query（服务端状态）**
- 数据获取与缓存
- 乐观更新
- IndexedDB 持久化

```typescript
// 持久化配置
const persister = createAsyncStoragePersister({
  storage: IndexedDB,
  key: 'react-query-cache',
})
```

**3. Zustand（客户端状态）**
- 轻量级局部状态
- 支持 Immer 不可变更新

#### 2.3 实时通信架构（Socket.IO）
```typescript
// contexts/socket.tsx
export const SocketProvider: React.FC = ({ children }) => {
  const socketManagerRef = useRef<SocketIOManager | null>(null)
  
  // 初始化 Socket 连接
  const socketManager = new SocketIOManager({
    serverUrl: process.env.NODE_ENV === 'development'
      ? 'http://localhost:57988'
      : window.location.origin,
    autoConnect: false
  })
  
  // 事件监听：connect, disconnect, connect_error
  // ...
}
```

**特点**：
- 自动重连机制（最多 5 次）
- 连接状态管理
- 错误处理与 UI 提示

### 3. 画布引擎选择

项目集成了三种画布引擎：

| 引擎 | 用途 | 特点 |
|------|------|------|
| **Excalidraw** | 手绘风格白板 | 协作友好、轻量 |
| **tldraw** | 专业绘图工具 | 功能丰富、可定制 |
| **XYFlow** | 节点流程图 | 适合 Agent 编排可视化 |

### 4. 组件设计模式

**1. 组合组件（Composition）**
```typescript
// ChatTextarea 组件
<ChatTextarea
  messages={messages}
  pending={isPending}
  onSendMessages={(messages, configs) => {
    // 发送消息逻辑
  }}
/>
```

**2. 受控组件 + Hooks**
- 使用 `ahooks` 的 `useDrop` 处理拖拽
- `useTranslation` 支持多语言
- 自定义 Hooks 封装业务逻辑

### 5. 构建与部署

**开发模式**：
```bash
npm run dev:react   # Vite dev server (端口 5174)
# API 代理到 http://127.0.0.1:57988
```

**生产构建**：
```bash
npm run build       # 构建到 react/dist/
# Electron 读取 dist/ 目录
```

---

## 后端架构分析

### 1. 目录结构
```
server/
├── routers/               # 路由层（API 端点）
│   ├── chat_router.py     # 聊天接口
│   ├── websocket_router.py # WebSocket 连接
│   ├── canvas.py          # 画布操作
│   ├── config_router.py   # 配置管理
│   ├── image_router.py    # 图像处理
│   ├── settings.py        # 设置接口
│   └── workspace.py       # 工作空间
├── services/              # 业务逻辑层
│   ├── chat_service.py    # 聊天服务
│   ├── magic_service.py   # 魔法生成服务
│   ├── config_service.py  # 配置服务
│   ├── tool_service.py    # 工具管理
│   ├── db_service.py      # 数据库服务
│   ├── websocket_service.py # WebSocket 通信
│   ├── langgraph_service/ # LangGraph Agent
│   │   ├── agent_service.py
│   │   ├── agent_manager.py
│   │   └── StreamProcessor.py
│   └── OpenAIAgents_service/ # OpenAI Agents
├── tools/                 # 工具函数（LangChain Tools）
│   ├── generate_image_by_*.py  # 图像生成工具
│   ├── generate_video_by_*.py  # 视频生成工具
│   ├── write_plan.py      # 计划生成
│   └── comfy_dynamic.py   # ComfyUI 动态工具
├── models/                # 数据模型
│   ├── config_model.py    # 配置模型
│   ├── db_model.py        # 数据库模型
│   └── tool_model.py      # 工具模型
├── utils/                 # 工具函数
├── main.py                # FastAPI 应用入口
├── common.py              # 公共配置
└── requirements.txt       # 依赖清单
```

### 2. FastAPI 应用架构

#### 2.1 应用初始化
```python
# main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化
    await config_service.initialize()
    await tool_service.initialize()
    await broadcast_init_done()
    yield
    # 关闭时清理

app = FastAPI(lifespan=lifespan)

# 挂载路由
app.include_router(chat_router.router)
app.include_router(canvas.router)
app.include_router(config_router.router)
# ...

# 集成 Socket.IO
socket_app = socketio.ASGIApp(sio, other_asgi_app=app, socketio_path='/socket.io')
```

**关键点**：
- 使用 `lifespan` 管理启动/关闭生命周期
- Socket.IO 与 FastAPI 共存（ASGI 包装）
- 静态文件服务（React 构建产物）

#### 2.2 路由层设计
```python
# routers/chat_router.py
router = APIRouter(prefix="/api")

@router.post("/chat")
async def chat(request: Request):
    data = await request.json()
    await handle_chat(data)  # 异步处理
    return {"status": "done"}

@router.post("/cancel/{session_id}")
async def cancel_chat(session_id: str):
    task = get_stream_task(session_id)
    if task and not task.done():
        task.cancel()
    return {"status": "cancelled"}
```

**特点**：
- 立即返回响应（非阻塞）
- 真正的处理在后台异步任务
- 支持任务取消

#### 2.3 WebSocket 架构
```python
# routers/websocket_router.py
from services.websocket_state import sio

@sio.event
async def connect(sid, environ, auth):
    add_connection(sid, user_info)
    await sio.emit('connected', {'status': 'connected'}, room=sid)

@sio.event
async def disconnect(sid):
    remove_connection(sid)
```

**消息流**：
1. 客户端连接 → 分配 `sid`
2. 服务端处理请求 → 通过 `session_id` 找到 `sid`
3. 实时推送结果 → `sio.emit(event, data, room=sid)`

### 3. 业务逻辑层

#### 3.1 聊天服务流程
```python
# services/chat_service.py
async def handle_chat(data: Dict[str, Any]) -> None:
    messages = data.get('messages', [])
    session_id = data.get('session_id', '')
    text_model = data.get('text_model', {})
    tool_list = data.get('tool_list', [])
    
    # 1. 保存会话到数据库
    await db_service.create_chat_session(session_id, ...)
    await db_service.create_message(session_id, ...)
    
    # 2. 创建 Agent 任务
    task = asyncio.create_task(
        langgraph_multi_agent(messages, canvas_id, session_id, text_model, tool_list)
    )
    
    # 3. 注册任务（用于取消）
    add_stream_task(session_id, task)
    
    try:
        await task
    except asyncio.exceptions.CancelledError:
        print(f"Session {session_id} cancelled")
    finally:
        remove_stream_task(session_id)
        await send_to_websocket(session_id, {'type': 'done'})
```

**关键设计**：
- **任务管理**：支持中途取消
- **异常处理**：保证资源清理
- **数据库持久化**：所有消息记录

#### 3.2 魔法生成服务
```python
# services/magic_service.py
async def handle_magic(data: Dict[str, Any]) -> None:
    # 使用 OpenAI Agents 服务
    task = asyncio.create_task(
        _process_magic_generation(messages, session_id, canvas_id)
    )
    # 类似 chat_service 的流程
```

**区别**：
- Magic 模式使用 OpenAI Agents（不同于 LangGraph）
- 更快的响应，适合简单生成

### 4. Agent 系统（LangGraph）

#### 4.1 多智能体架构
```python
# services/langgraph_service/agent_service.py
async def langgraph_multi_agent(
    messages: List[Dict[str, Any]],
    canvas_id: str,
    session_id: str,
    text_model: ModelInfo,
    tool_list: List[ToolInfoJson],
    system_prompt: Optional[str] = None
) -> None:
    # 1. 修复消息历史（移除不完整的工具调用）
    fixed_messages = _fix_chat_history(messages)
    
    # 2. 创建文本模型实例
    text_model_instance = _create_text_model(text_model)
    
    # 3. 创建智能体
    agents = AgentManager.create_agents(
        text_model_instance,
        tool_list,
        system_prompt
    )
    
    # 4. 创建智能体群组（Swarm）
    swarm = create_swarm(
        agents=agents,
        default_active_agent=last_agent
    )
    
    # 5. 流式处理
    processor = StreamProcessor(session_id, db_service, send_to_websocket)
    await processor.process_stream(swarm, fixed_messages, context)
```

**核心概念**：
- **Agent**: 具有特定职责的智能体（如 Planner、Image Generator）
- **Swarm**: 多个 Agent 协同工作
- **StreamProcessor**: 处理流式输出并推送到前端

#### 4.2 工具注册机制
```python
# services/tool_service.py
TOOL_MAPPING: Dict[str, ToolInfo] = {
    "generate_image_by_gpt_image_1_jaaz": {
        "display_name": "GPT Image 1",
        "type": "image",
        "provider": "jaaz",
        "tool_function": generate_image_by_gpt_image_1_jaaz,
    },
    # ... 更多工具
}

class ToolService:
    async def initialize(self):
        # 根据 API Key 注册工具
        for provider_name, provider_config in config_service.app_config.items():
            if provider_config.get("api_key"):
                for tool_id, tool_info in TOOL_MAPPING.items():
                    if tool_info.get("provider") == provider_name:
                        self.register_tool(tool_id, tool_info)
        
        # 注册 ComfyUI 动态工具
        await register_comfy_tools()
```

**动态工具系统**：
- 仅注册有 API Key 的工具
- 支持 ComfyUI 工作流动态生成工具

### 5. 数据库层

**数据库选择**: SQLite（异步 aiosqlite）

**核心表结构**（推测）：
- `chat_sessions`: 会话信息
- `messages`: 消息记录
- `canvas`: 画布数据
- `comfy_workflows`: ComfyUI 工作流
- `workspace`: 工作空间配置

### 6. 配置管理

```python
# services/config_service.py
class ConfigService:
    def __init__(self):
        self.app_config = {}
    
    async def initialize(self):
        # 从环境变量/文件加载配置
        self.app_config = {
            "openai": {"api_key": "..."},
            "replicate": {"api_key": "..."},
            "ollama": {"url": "http://localhost:11434"},
            "comfyui": {"url": "http://localhost:8188"},
            # ...
        }
```

**配置来源**：
1. 用户 UI 设置
2. 环境变量
3. 配置文件（TOML）

---

## 前后端交互机制

### 1. 通信协议

#### 1.1 HTTP REST API
**用途**: 请求-响应模式

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/chat` | POST | 发送聊天消息 |
| `/api/magic` | POST | 魔法生成 |
| `/api/cancel/{session_id}` | POST | 取消任务 |
| `/api/canvas` | GET/POST | 画布操作 |
| `/api/config` | GET/PUT | 配置管理 |
| `/api/upload` | POST | 文件上传 |

**请求示例**：
```typescript
// api/chat.ts
export const sendMessages = async (payload: {
  sessionId: string
  canvasId: string
  newMessages: Message[]
  textModel: Model
  toolList: ToolInfo[]
}) => {
  const response = await fetch(`/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      messages: payload.newMessages,
      canvas_id: payload.canvasId,
      session_id: payload.sessionId,
      text_model: payload.textModel,
      tool_list: payload.toolList,
    }),
  })
  return await response.json()
}
```

#### 1.2 WebSocket（Socket.IO）
**用途**: 实时双向通信

**前端实现**：
```typescript
// lib/socket.ts
export class SocketIOManager {
  private socket: Socket
  
  async connect() {
    this.socket = io(serverUrl, {
      autoConnect: false,
      transports: ['websocket'],
    })
    
    this.socket.on('connected', (data) => {
      console.log('Connected:', data)
    })
    
    this.socket.on('message', (data) => {
      // 处理服务端推送的消息
    })
  }
}
```

**后端推送**：
```python
# services/websocket_service.py
async def send_to_websocket(session_id: str, data: Dict):
    sid = get_sid_by_session_id(session_id)
    if sid:
        await sio.emit('message', data, room=sid)
```

### 2. 数据流详解

#### 2.1 聊天生成流程
```
┌─────────┐                ┌──────────┐                ┌─────────┐
│ 前端 UI │                │ FastAPI  │                │ LangGraph│
└────┬────┘                └────┬─────┘                └────┬────┘
     │                          │                           │
     │ POST /api/chat           │                           │
     ├─────────────────────────>│                           │
     │ {messages, session_id}   │                           │
     │                          │                           │
     │ {"status": "done"}       │                           │
     │<─────────────────────────┤                           │
     │                          │                           │
     │                          │ create_task(              │
     │                          │   langgraph_multi_agent)  │
     │                          ├──────────────────────────>│
     │                          │                           │
     │                          │                           │ Agent 处理
     │                          │                           ├──────────┐
     │                          │                           │          │
     │                          │                           │<─────────┘
     │                          │                           │
     │                          │                           │ 工具调用
     │                          │<──────────────────────────┤
     │                          │                           │
     │   WebSocket: {type: ...} │                           │
     │<─────────────────────────┤                           │
     │                          │                           │
     │   WebSocket: {type: ...} │                           │
     │<─────────────────────────┤                           │
     │                          │                           │
     │   WebSocket: {done}      │                           │
     │<─────────────────────────┤                           │
     │                          │                           │
```

**推送消息类型**：
- `type: 'text'`: 文本流式输出
- `type: 'tool_call'`: 工具调用通知
- `type: 'image'`: 生成的图像 URL
- `type: 'video'`: 生成的视频 URL
- `type: 'done'`: 完成标志

#### 2.2 图像生成流程
```python
# tools/generate_image_by_gpt_image_1_jaaz.py
async def generate_image_by_gpt_image_1_jaaz(
    prompt: str,
    context: ContextInfo
) -> str:
    session_id = context['session_id']
    
    # 1. 调用 Jaaz API
    response = await http_client.post(
        f"{BASE_API_URL}/api/generate/gpt-image-1",
        json={"prompt": prompt, "session_id": session_id}
    )
    
    # 2. 轮询结果
    task_id = response['task_id']
    while True:
        status = await check_task_status(task_id)
        if status['status'] == 'completed':
            image_url = status['image_url']
            break
        await asyncio.sleep(2)
    
    # 3. 推送到前端
    await send_to_websocket(session_id, {
        'type': 'image',
        'url': image_url,
        'tool_name': 'GPT Image 1'
    })
    
    return f"Image generated: {image_url}"
```

### 3. 状态同步

**前端状态**：
```typescript
// 消息列表
const [messages, setMessages] = useState<Message[]>([])

// 监听 WebSocket
useEffect(() => {
  socket.on('message', (data) => {
    if (data.type === 'text') {
      // 更新最后一条消息
      setMessages(prev => {
        const last = prev[prev.length - 1]
        return [...prev.slice(0, -1), { ...last, content: last.content + data.text }]
      })
    } else if (data.type === 'image') {
      // 添加图像消息
      setMessages(prev => [...prev, { role: 'assistant', images: [data.url] }])
    }
  })
}, [])
```

---

## 核心功能模块

### 1. 无限画布（Infinite Canvas）

**技术选型**: Excalidraw / tldraw

**功能**：
- 无限缩放与平移
- 多种绘图工具（矩形、箭头、文本）
- 图像/视频元素拖放
- 协作编辑（实时同步）

**数据结构**（Excalidraw）：
```typescript
interface CanvasElement {
  id: string
  type: 'rectangle' | 'arrow' | 'text' | 'image'
  x: number
  y: number
  width: number
  height: number
  // ...更多属性
}
```

### 2. Agent 工作室（Agent Studio）

**路径**: `/agent_studio`

**功能**：
- 可视化 Agent 编排（使用 XYFlow）
- 自定义工作流
- 调试 Agent 执行过程

### 3. 知识库（Knowledge Base）

**路径**: `/knowledge`

**功能**：
- 上传文档（PDF、Markdown）
- 向量化存储（用于 RAG）
- 为 Agent 提供上下文

### 4. 资产管理（Assets）

**路径**: `/assets`

**功能**：
- 管理生成的图像/视频
- 本地存储路径
- 标签与分类

### 5. ComfyUI 集成

**安装器**：
```javascript
// electron/comfyUIInstaller.js
async function installComfyUI() {
  // 1. 下载 ComfyUI 压缩包
  // 2. 解压到用户目录
  // 3. 安装依赖（Python venv）
}
```

**进程管理**：
```javascript
// electron/comfyUIManager.js
let comfyUIProcess = null

function startComfyUI() {
  comfyUIProcess = spawn('python', ['main.py'], {
    cwd: comfyUIPath
  })
}
```

**工具动态生成**：
```python
# tools/comfy_dynamic.py
def build_tool(workflow: Dict) -> BaseTool:
    """从 ComfyUI 工作流生成 LangChain 工具"""
    async def tool_function(prompt: str, context: ContextInfo) -> str:
        # 1. 调用 ComfyUI API
        response = await comfyui_client.queue_prompt(workflow)
        # 2. 等待完成
        # 3. 返回结果
    
    return StructuredTool.from_function(
        func=tool_function,
        name=f"comfyui_{workflow['name']}",
        description=workflow.get('description', '')
    )
```

---

## 数据流与状态管理

### 1. 应用状态层次

```
┌──────────────────────────────────────────┐
│          IndexedDB 持久化                 │
│    (TanStack Query Cache)                │
└─────────────────┬────────────────────────┘
                  │
┌─────────────────▼────────────────────────┐
│       TanStack Query                     │
│   (服务端数据 + 缓存)                     │
│   - Canvas 列表                          │
│   - Chat 历史                            │
│   - 配置数据                             │
└─────────────────┬────────────────────────┘
                  │
┌─────────────────▼────────────────────────┐
│        React Context                     │
│   - Socket 连接状态                       │
│   - 用户认证信息                          │
│   - 全局配置                             │
└─────────────────┬────────────────────────┘
                  │
┌─────────────────▼────────────────────────┐
│         Zustand Store                    │
│   - UI 状态（侧边栏、对话框）              │
│   - 临时数据                             │
└──────────────────────────────────────────┘
```

### 2. 数据获取模式

**乐观更新示例**：
```typescript
const { mutate: createCanvasMutation } = useMutation({
  mutationFn: createCanvas,
  onMutate: async (newCanvas) => {
    // 1. 取消正在进行的查询
    await queryClient.cancelQueries({ queryKey: ['canvasList'] })
    
    // 2. 快照当前数据
    const previousCanvases = queryClient.getQueryData(['canvasList'])
    
    // 3. 乐观更新 UI
    queryClient.setQueryData(['canvasList'], (old) => [...old, newCanvas])
    
    return { previousCanvases }
  },
  onError: (err, newCanvas, context) => {
    // 4. 错误时回滚
    queryClient.setQueryData(['canvasList'], context.previousCanvases)
  },
  onSettled: () => {
    // 5. 重新获取数据
    queryClient.invalidateQueries({ queryKey: ['canvasList'] })
  },
})
```

---

## AI Agent 架构

### 1. LangGraph Agent 系统

**核心概念**：
- **Node（节点）**: 代表一个处理步骤（调用 LLM、执行工具）
- **Edge（边）**: 节点间的转移条件
- **State（状态）**: 整个图的数据流

**Agent 类型**：
1. **Planner Agent**: 分解任务、制定计划
2. **Image Generator Agent**: 图像生成
3. **Video Generator Agent**: 视频生成
4. **Editor Agent**: 图像编辑

**Agent 管理器**：
```python
# services/langgraph_service/agent_manager.py
class AgentManager:
    @staticmethod
    def create_agents(
        text_model: Any,
        tool_list: List[ToolInfoJson],
        system_prompt: str
    ) -> List[Agent]:
        agents = []
        
        # 1. Planner Agent（必须）
        agents.append(Agent(
            name='Planner',
            model=text_model,
            tools=[write_plan_tool],
            instructions=system_prompt
        ))
        
        # 2. 根据 tool_list 创建专用 Agent
        for tool_info in tool_list:
            tool_function = tool_service.get_tool(tool_info['model'])
            if tool_info['type'] == 'image':
                agents.append(Agent(
                    name=f'ImageGenerator_{tool_info["model"]}',
                    model=text_model,
                    tools=[tool_function],
                    instructions='Generate high-quality images...'
                ))
        
        return agents
```

### 2. Stream 处理器

```python
# services/langgraph_service/StreamProcessor.py
class StreamProcessor:
    async def process_stream(self, swarm, messages, context):
        async for event in swarm.astream(
            {"messages": messages},
            config={"configurable": {"context": context}}
        ):
            # 处理不同类型的事件
            if event['type'] == 'on_chat_model_stream':
                # 文本流式输出
                await self.send_text_chunk(event['data']['chunk'])
            elif event['type'] == 'on_tool_start':
                # 工具调用开始
                await self.send_tool_call_start(event['data'])
            elif event['type'] == 'on_tool_end':
                # 工具调用结束
                await self.send_tool_result(event['data'])
```

### 3. 工具执行上下文

所有工具函数接收 `ContextInfo`：
```python
class ContextInfo(TypedDict):
    canvas_id: str      # 画布 ID
    session_id: str     # 会话 ID（用于 WebSocket 推送）
    tool_list: List[ToolInfoJson]  # 可用工具列表
```

**工具实现模板**：
```python
async def generate_image_by_xxx(
    prompt: str,
    context: ContextInfo,
    width: int = 1024,
    height: int = 1024
) -> str:
    """
    生成图像的标准工具函数
    
    Args:
        prompt: 提示词
        context: 上下文信息
        width/height: 图像尺寸
    
    Returns:
        str: 返回给 Agent 的描述文本
    """
    session_id = context['session_id']
    
    # 1. 调用 API
    image_url = await call_image_api(prompt, width, height)
    
    # 2. 推送到前端
    await send_to_websocket(session_id, {
        'type': 'image',
        'url': image_url,
        'metadata': {'width': width, 'height': height}
    })
    
    # 3. 返回描述（给 LLM）
    return f"Successfully generated image at {image_url}"
```

---

## 工具与模型集成

### 1. 支持的图像模型

| 模型 | Provider | API |
|------|----------|-----|
| GPT Image 1 | jaaz | Jaaz 自有 API |
| Imagen 4 | jaaz / replicate | Google Imagen |
| Recraft v3 | jaaz / replicate | Recraft API |
| Ideogram 3 | jaaz | Ideogram API |
| Flux Kontext Pro/Max | jaaz / replicate | Flux API |
| Midjourney | jaaz | Midjourney API |
| Doubao Seedream 3 | jaaz / volces | 字节豆包 |

### 2. 支持的视频模型

| 模型 | Provider | API |
|------|----------|-----|
| Seedance v1 | jaaz / volces | 字节豆包 |
| Kling v2.1 | jaaz | 快手可灵 |
| Hailuo 02 | jaaz | 海螺 AI |
| Veo3 Fast | jaaz | Google Veo |

### 3. 支持的文本模型

| 模型 | Provider | 部署方式 |
|------|----------|----------|
| GPT-4o / GPT-4 | OpenAI | 云端 API |
| Claude 3.5 | Anthropic | 云端 API |
| Llama 3 / Mistral | Ollama | 本地运行 |

### 4. API Key 管理

**配置界面** (`/settings`):
```typescript
// components/settings/dialog.tsx
<Input
  type="password"
  placeholder="sk-..."
  value={config.openai?.api_key || ''}
  onChange={(e) => updateConfig('openai', 'api_key', e.target.value)}
/>
```

**后端存储**:
```python
# 存储在用户目录
config_path = os.path.join(user_data_dir, 'config.toml')

# 示例配置
[openai]
api_key = "sk-..."
base_url = "https://api.openai.com/v1"

[replicate]
api_key = "r8_..."

[ollama]
url = "http://localhost:11434"
```

---

## 部署架构

### 1. Electron 应用打包

**构建流程**：
```bash
# 1. 构建前端
cd react && npm run build
# 输出: react/dist/

# 2. 构建后端
cd server && pyinstaller main.spec
# 输出: server/dist/main/main.exe (Windows)

# 3. 打包 Electron
npm run build:electron
# 输出: dist/Jaaz-1.0.30.dmg (macOS)
```

**目录结构**（打包后）：
```
Jaaz.app/
├── Contents/
│   ├── MacOS/
│   │   └── Jaaz              # Electron 主进程
│   ├── Resources/
│   │   ├── app.asar          # Electron 代码
│   │   ├── react/dist/       # 前端构建产物
│   │   ├── server/dist/main/ # Python 可执行文件
│   │   │   └── main          # PyInstaller 打包
│   │   └── assets/
```

### 2. 启动流程

```javascript
// electron/main.js 启动序列
app.whenReady().then(async () => {
  // 1. 查找可用端口
  const port = await findAvailablePort(57988)
  
  // 2. 启动 Python 服务
  pyProc = spawn(pythonExecutable, ['--port', port], { env })
  
  // 3. 等待服务就绪
  while (true) {
    const status = await fetch(`http://127.0.0.1:${port}`)
    if (status.ok) break
    await sleep(1000)
  }
  
  // 4. 创建窗口
  createWindow(port)
})
```

### 3. 自动更新机制

**electron-updater**：
```javascript
const { autoUpdater } = require('electron-updater')

autoUpdater.on('update-available', (info) => {
  console.log('Update available:', info.version)
  autoUpdater.downloadUpdate()
})

autoUpdater.on('update-downloaded', (info) => {
  // 通知前端
  mainWindow.webContents.send('update-downloaded', info)
})

// 前端触发重启
ipcMain.handle('restart-and-install', () => {
  autoUpdater.quitAndInstall()
})
```

### 4. 跨平台适配

**平台差异**：
```javascript
const isWindows = process.platform === 'win32'
const isMac = process.platform === 'darwin'

// Python 可执行文件路径
const pythonExecutable = app.isPackaged
  ? path.join(process.resourcesPath, 'server/dist/main', 
      isWindows ? 'main.exe' : 'main')
  : 'python'
```

---

## 视觉类 Agent 项目建议

基于 Jaaz 项目的深入分析，以下是构建视觉类 Agent 项目的关键建议：

### 1. 核心架构选择

#### 推荐架构：
```
Electron（可选）+ React + FastAPI + LangGraph
```

**为什么？**
- **Electron**: 如果需要桌面应用；Web 应用可省略
- **React**: 成熟的 UI 框架，丰富的生态
- **FastAPI**: 高性能异步框架，原生支持 WebSocket
- **LangGraph**: 专业的 Agent 编排工具，比自己实现状态机高效

### 2. 前端技术栈建议

| 技术 | 用途 | 必选？ |
|------|------|--------|
| **TanStack Query** | 数据获取与缓存 | ✅ |
| **Socket.IO Client** | 实时通信 | ✅ |
| **Zustand** | 轻量状态管理 | ✅ |
| **Excalidraw / tldraw** | 画布引擎 | 可选 |
| **Tailwind CSS** | 快速样式开发 | ✅ |
| **Radix UI** | 无障碍组件库 | ✅ |

**关键设计**：
1. **分离服务端状态和 UI 状态**
   - 服务端状态 → TanStack Query
   - UI 状态 → Zustand / React Context

2. **实时通信架构**
   ```typescript
   // 核心模式
   HTTP POST /api/generate → 立即返回 {"task_id": "..."}
   WebSocket 监听 → 接收流式结果
   ```

3. **组件化画布**
   - 独立的画布组件库
   - 支持插件式扩展（图像、视频、文本）

### 3. 后端技术栈建议

| 技术 | 用途 | 必选？ |
|------|------|--------|
| **FastAPI** | Web 框架 | ✅ |
| **Socket.IO (Python)** | WebSocket | ✅ |
| **LangGraph** | Agent 编排 | ✅ |
| **LangChain** | LLM 工具链 | ✅ |
| **SQLite / PostgreSQL** | 数据库 | ✅ |
| **Celery（可选）** | 后台任务队列 | 对于大规模部署 |

**关键设计**：
1. **异步优先**
   ```python
   # 所有 I/O 操作使用 async/await
   async def handle_generation(data):
       result = await call_ai_model(data)
       await db.save(result)
       await send_to_websocket(session_id, result)
   ```

2. **任务管理系统**
   ```python
   # 支持取消和进度查询
   stream_tasks = {}  # session_id -> asyncio.Task
   
   async def cancel_task(session_id):
       task = stream_tasks.get(session_id)
       if task and not task.done():
           task.cancel()
   ```

3. **工具动态注册**
   ```python
   # 工具服务
   class ToolService:
       def __init__(self):
           self.tools = {}
       
       def register_tool(self, tool_id: str, tool_info: ToolInfo):
           """动态注册工具"""
           self.tools[tool_id] = tool_info
       
       async def initialize(self):
           """根据配置注册可用工具"""
           for provider, config in app_config.items():
               if config.get('api_key'):
                   self._register_provider_tools(provider)
   ```

4. **流式响应处理**
   ```python
   # 推荐使用 StreamProcessor 模式
   class StreamProcessor:
       async def process(self, generator):
           async for event in generator:
               await self.handle_event(event)
               await self.push_to_frontend(event)
   ```

### 4. Agent 系统设计建议

#### 4.1 Agent 角色划分

**推荐的 Agent 架构**：
```python
# 基于职责分离的多智能体系统
agents = [
    {
        "name": "Coordinator",
        "role": "任务协调",
        "tools": ["task_planning", "agent_routing"],
        "description": "分析用户需求，分配给合适的专业 Agent"
    },
    {
        "name": "ImageGenerator", 
        "role": "图像生成",
        "tools": ["flux_pro", "midjourney", "imagen"],
        "description": "处理所有图像生成任务"
    },
    {
        "name": "VideoGenerator",
        "role": "视频生成", 
        "tools": ["kling", "veo3", "hailuo"],
        "description": "处理视频生成任务"
    },
    {
        "name": "Editor",
        "role": "内容编辑",
        "tools": ["image_edit", "video_edit", "style_transfer"],
        "description": "修改和优化已生成的内容"
    }
]
```

**为什么这样设计？**
1. **职责明确**：每个 Agent 只关注自己的领域
2. **易于扩展**：新增功能只需添加新 Agent
3. **并行处理**：多个 Agent 可以同时工作
4. **工具隔离**：避免工具调用冲突

#### 4.2 LangGraph 工作流设计

```python
from langgraph.graph import StateGraph, END

# 定义状态
class AgentState(TypedDict):
    messages: List[BaseMessage]
    next_agent: str
    context: Dict[str, Any]
    results: List[Dict[str, Any]]

# 构建图
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("coordinator", coordinator_agent)
workflow.add_node("image_gen", image_generator_agent)
workflow.add_node("video_gen", video_generator_agent)
workflow.add_node("editor", editor_agent)

# 定义路由逻辑
def route_next_agent(state: AgentState) -> str:
    """根据 next_agent 字段路由"""
    if state['next_agent'] == 'END':
        return END
    return state['next_agent']

# 添加边
workflow.set_entry_point("coordinator")
workflow.add_conditional_edges(
    "coordinator",
    route_next_agent,
    {
        "image_gen": "image_gen",
        "video_gen": "video_gen", 
        "editor": "editor",
        END: END
    }
)

# 编译图
app = workflow.compile()
```

#### 4.3 工具函数标准化

**所有工具函数遵循统一接口**：
```python
from typing import TypedDict, Any
from langchain.tools import BaseTool

class ContextInfo(TypedDict):
    """工具执行上下文"""
    session_id: str      # 会话 ID（用于 WebSocket 推送）
    canvas_id: str       # 画布 ID（用于资产关联）
    user_id: str         # 用户 ID（用于权限控制）
    metadata: Dict[str, Any]  # 扩展元数据

async def tool_function_template(
    # 必需参数
    prompt: str,
    context: ContextInfo,
    # 可选参数
    width: int = 1024,
    height: int = 1024,
    **kwargs
) -> str:
    """
    工具函数模板
    
    Args:
        prompt: 用户提示词
        context: 执行上下文
        width/height: 生成参数
        **kwargs: 其他模型特定参数
    
    Returns:
        str: 返回给 LLM 的描述文本
    """
    session_id = context['session_id']
    
    try:
        # 1. 参数验证
        if not prompt:
            raise ValueError("Prompt is required")
        
        # 2. 调用 AI 模型
        result = await call_ai_model_api(
            prompt=prompt,
            width=width,
            height=height,
            **kwargs
        )
        
        # 3. 保存到数据库
        asset_id = await save_asset_to_db(
            canvas_id=context['canvas_id'],
            asset_type='image',
            url=result['url'],
            metadata={'width': width, 'height': height}
        )
        
        # 4. 推送到前端
        await send_to_websocket(session_id, {
            'type': 'image',
            'url': result['url'],
            'asset_id': asset_id,
            'tool_name': 'xxx_model',
            'metadata': {'width': width, 'height': height}
        })
        
        # 5. 返回描述（给 LLM）
        return f"Successfully generated image with dimensions {width}x{height}. Asset ID: {asset_id}"
        
    except Exception as e:
        # 错误处理
        await send_to_websocket(session_id, {
            'type': 'error',
            'message': str(e),
            'tool_name': 'xxx_model'
        })
        return f"Error: {str(e)}"
```

**工具注册标准**：
```python
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

class ImageGenerationInput(BaseModel):
    """工具输入模型"""
    prompt: str = Field(description="图像描述提示词")
    width: int = Field(default=1024, description="图像宽度")
    height: int = Field(default=1024, description="图像高度")
    style: str = Field(default="realistic", description="图像风格")

# 创建工具
image_tool = StructuredTool.from_function(
    func=tool_function_template,
    name="generate_image_flux_pro",
    description="使用 Flux Pro 生成高质量图像。支持多种风格和尺寸。",
    args_schema=ImageGenerationInput,
    return_direct=False,  # 不直接返回，由 Agent 决定
)
```

### 5. 数据库设计建议

#### 5.1 核心表结构

```sql
-- 1. 用户表（如果需要多用户）
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 画布表
CREATE TABLE canvases (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    thumbnail TEXT,  -- 缩略图 URL
    canvas_data JSON,  -- Excalidraw/tldraw 数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 3. 会话表
CREATE TABLE chat_sessions (
    id TEXT PRIMARY KEY,
    canvas_id TEXT NOT NULL,
    title TEXT,
    agent_config JSON,  -- Agent 配置快照
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (canvas_id) REFERENCES canvases(id)
);

-- 4. 消息表
CREATE TABLE messages (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,  -- 'user' | 'assistant' | 'system'
    content TEXT,
    tool_calls JSON,  -- 工具调用记录
    images JSON,  -- 图像 URL 列表
    videos JSON,  -- 视频 URL 列表
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

-- 5. 资产表（生成的图像/视频）
CREATE TABLE assets (
    id TEXT PRIMARY KEY,
    canvas_id TEXT NOT NULL,
    session_id TEXT,
    asset_type TEXT NOT NULL,  -- 'image' | 'video'
    url TEXT NOT NULL,
    local_path TEXT,  -- 本地存储路径
    tool_name TEXT,  -- 生成工具
    prompt TEXT,  -- 原始提示词
    metadata JSON,  -- 宽高、时长等
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (canvas_id) REFERENCES canvases(id),
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

-- 6. 工具调用日志表
CREATE TABLE tool_executions (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    input_params JSON,
    output_result TEXT,
    status TEXT,  -- 'success' | 'failed' | 'cancelled'
    duration_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

-- 7. 配置表
CREATE TABLE app_config (
    key TEXT PRIMARY KEY,
    value JSON,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 5.2 数据库服务封装

```python
# services/db_service.py
import aiosqlite
from typing import List, Dict, Any, Optional

class DatabaseService:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.db: Optional[aiosqlite.Connection] = None
    
    async def initialize(self):
        """初始化数据库连接"""
        self.db = await aiosqlite.connect(self.db_path)
        self.db.row_factory = aiosqlite.Row
        await self._create_tables()
    
    async def _create_tables(self):
        """创建表结构"""
        # 执行上面的 SQL 语句
        pass
    
    # Canvas 操作
    async def create_canvas(
        self, 
        canvas_id: str, 
        user_id: str, 
        title: str
    ) -> Dict[str, Any]:
        async with self.db.execute(
            "INSERT INTO canvases (id, user_id, title) VALUES (?, ?, ?)",
            (canvas_id, user_id, title)
        ) as cursor:
            await self.db.commit()
            return await self.get_canvas(canvas_id)
    
    async def get_canvas(self, canvas_id: str) -> Optional[Dict[str, Any]]:
        async with self.db.execute(
            "SELECT * FROM canvases WHERE id = ?",
            (canvas_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def update_canvas_data(
        self, 
        canvas_id: str, 
        canvas_data: Dict[str, Any]
    ):
        await self.db.execute(
            "UPDATE canvases SET canvas_data = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (json.dumps(canvas_data), canvas_id)
        )
        await self.db.commit()
    
    # Session 操作
    async def create_chat_session(
        self,
        session_id: str,
        canvas_id: str,
        title: Optional[str] = None,
        agent_config: Optional[Dict] = None
    ):
        await self.db.execute(
            "INSERT INTO chat_sessions (id, canvas_id, title, agent_config) VALUES (?, ?, ?, ?)",
            (session_id, canvas_id, title, json.dumps(agent_config or {}))
        )
        await self.db.commit()
    
    # Message 操作
    async def create_message(
        self,
        message_id: str,
        session_id: str,
        role: str,
        content: str,
        tool_calls: Optional[List[Dict]] = None,
        images: Optional[List[str]] = None,
        videos: Optional[List[str]] = None
    ):
        await self.db.execute(
            """INSERT INTO messages 
               (id, session_id, role, content, tool_calls, images, videos) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                message_id, session_id, role, content,
                json.dumps(tool_calls or []),
                json.dumps(images or []),
                json.dumps(videos or [])
            )
        )
        await self.db.commit()
    
    async def get_session_messages(
        self, 
        session_id: str
    ) -> List[Dict[str, Any]]:
        async with self.db.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC",
            (session_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    # Asset 操作
    async def create_asset(
        self,
        asset_id: str,
        canvas_id: str,
        session_id: str,
        asset_type: str,
        url: str,
        tool_name: str,
        prompt: str,
        metadata: Optional[Dict] = None
    ) -> str:
        await self.db.execute(
            """INSERT INTO assets 
               (id, canvas_id, session_id, asset_type, url, tool_name, prompt, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                asset_id, canvas_id, session_id, asset_type, 
                url, tool_name, prompt, json.dumps(metadata or {})
            )
        )
        await self.db.commit()
        return asset_id
    
    async def get_canvas_assets(
        self, 
        canvas_id: str,
        asset_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if asset_type:
            query = "SELECT * FROM assets WHERE canvas_id = ? AND asset_type = ? ORDER BY created_at DESC"
            params = (canvas_id, asset_type)
        else:
            query = "SELECT * FROM assets WHERE canvas_id = ? ORDER BY created_at DESC"
            params = (canvas_id,)
        
        async with self.db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    # 工具执行日志
    async def log_tool_execution(
        self,
        execution_id: str,
        session_id: str,
        tool_name: str,
        input_params: Dict,
        output_result: Optional[str] = None,
        status: str = 'success',
        duration_ms: Optional[int] = None,
        error_message: Optional[str] = None
    ):
        await self.db.execute(
            """INSERT INTO tool_executions 
               (id, session_id, tool_name, input_params, output_result, status, duration_ms, error_message)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                execution_id, session_id, tool_name,
                json.dumps(input_params), output_result,
                status, duration_ms, error_message
            )
        )
        await self.db.commit()
    
    async def close(self):
        """关闭数据库连接"""
        if self.db:
            await self.db.close()
```

### 6. 性能优化建议

#### 6.1 前端优化

**1. 代码分割与懒加载**
```typescript
// routes 使用 lazy 加载
import { lazy } from '@tanstack/react-router'

const Route = createFileRoute('/canvas/$id')({
  component: lazy(() => import('./canvas-page')),
})
```

**2. 虚拟滚动**
```typescript
// 消息列表使用虚拟滚动
import { useVirtualizer } from '@tanstack/react-virtual'

const MessageList = () => {
  const virtualizer = useVirtualizer({
    count: messages.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 100,
  })
}
```

**3. 图像懒加载与占位符**
```typescript
<img 
  src={imageUrl} 
  loading="lazy"
  placeholder="blur"
  onLoad={handleImageLoad}
/>
```

**4. WebSocket 消息批处理**
```typescript
// 避免频繁渲染
const messageBuffer: Message[] = []
let flushTimer: NodeJS.Timeout

socket.on('message', (data) => {
  messageBuffer.push(data)
  
  clearTimeout(flushTimer)
  flushTimer = setTimeout(() => {
    setMessages(prev => [...prev, ...messageBuffer])
    messageBuffer.length = 0
  }, 50) // 50ms 批处理
})
```

#### 6.2 后端优化

**1. 数据库连接池**
```python
# 使用 aiosqlite 连接池
from contextlib import asynccontextmanager

class DatabasePool:
    def __init__(self, db_path: str, max_connections: int = 5):
        self.db_path = db_path
        self.pool: List[aiosqlite.Connection] = []
        self.max_connections = max_connections
    
    @asynccontextmanager
    async def get_connection(self):
        if not self.pool:
            conn = await aiosqlite.connect(self.db_path)
        else:
            conn = self.pool.pop()
        
        try:
            yield conn
        finally:
            if len(self.pool) < self.max_connections:
                self.pool.append(conn)
            else:
                await conn.close()
```

**2. API 调用缓存**
```python
from functools import lru_cache
import hashlib

class AIModelCache:
    def __init__(self):
        self.cache = {}
    
    def cache_key(self, prompt: str, **params) -> str:
        data = f"{prompt}_{params}".encode()
        return hashlib.md5(data).hexdigest()
    
    async def get_or_generate(
        self, 
        prompt: str, 
        generator_func,
        **params
    ):
        key = self.cache_key(prompt, **params)
        
        if key in self.cache:
            return self.cache[key]
        
        result = await generator_func(prompt, **params)
        self.cache[key] = result
        return result
```

**3. 并发限制**
```python
import asyncio
from asyncio import Semaphore

# 限制并发 API 调用数
API_SEMAPHORE = Semaphore(5)

async def call_ai_model(prompt: str):
    async with API_SEMAPHORE:
        result = await actual_api_call(prompt)
        return result
```

**4. 流式响应优化**
```python
# 使用 StreamingResponse
from fastapi.responses import StreamingResponse

@router.get("/stream")
async def stream_generation():
    async def generate():
        async for chunk in ai_model.generate_stream(prompt):
            yield f"data: {json.dumps(chunk)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

#### 6.3 资源管理

**1. 图像/视频存储策略**
```python
import os
from pathlib import Path

class AssetManager:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def get_asset_path(
        self, 
        canvas_id: str, 
        asset_id: str, 
        asset_type: str
    ) -> Path:
        """
        组织结构:
        assets/
          └── canvas_{canvas_id}/
              ├── images/
              │   └── {asset_id}.png
              └── videos/
                  └── {asset_id}.mp4
        """
        canvas_dir = self.base_dir / f"canvas_{canvas_id}" / f"{asset_type}s"
        canvas_dir.mkdir(parents=True, exist_ok=True)
        
        ext = '.png' if asset_type == 'image' else '.mp4'
        return canvas_dir / f"{asset_id}{ext}"
    
    async def save_asset(
        self,
        canvas_id: str,
        asset_id: str,
        asset_type: str,
        data: bytes
    ) -> str:
        """保存资产并返回相对路径"""
        path = self.get_asset_path(canvas_id, asset_id, asset_type)
        
        async with aiofiles.open(path, 'wb') as f:
            await f.write(data)
        
        return str(path.relative_to(self.base_dir))
    
    def cleanup_canvas_assets(self, canvas_id: str):
        """删除画布相关的所有资产"""
        canvas_dir = self.base_dir / f"canvas_{canvas_id}"
        if canvas_dir.exists():
            shutil.rmtree(canvas_dir)
```

**2. 临时文件清理**
```python
import tempfile
from contextlib import asynccontextmanager

@asynccontextmanager
async def temporary_file(suffix: str = ''):
    """自动清理的临时文件"""
    fd, path = tempfile.mkstemp(suffix=suffix)
    try:
        yield path
    finally:
        os.close(fd)
        if os.path.exists(path):
            os.remove(path)

# 使用示例
async with temporary_file(suffix='.png') as temp_path:
    await download_image(url, temp_path)
    await process_image(temp_path)
    # 自动清理
```

### 7. 开发流程建议

#### 7.1 项目初始化清单

**1. 前端项目**
```bash
# 创建 React + TypeScript 项目
npm create vite@latest my-agent-app -- --template react-ts

# 安装核心依赖
npm install @tanstack/react-router @tanstack/react-query
npm install socket.io-client zustand
npm install @radix-ui/react-* tailwindcss
npm install ahooks i18next react-i18next
```

**2. 后端项目**
```bash
# 创建项目目录
mkdir server && cd server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install fastapi uvicorn python-socketio
pip install langgraph langchain langchain-openai
pip install aiosqlite aiofiles httpx
pip install python-dotenv pydantic
```

**3. 项目结构模板**
```
my-agent-app/
├── frontend/                 # React 前端
│   ├── src/
│   │   ├── api/             # API 调用
│   │   ├── components/      # 组件
│   │   ├── contexts/        # Context
│   │   ├── hooks/           # 自定义 Hooks
│   │   ├── routes/          # 路由页面
│   │   ├── stores/          # Zustand stores
│   │   ├── types/           # TypeScript 类型
│   │   └── utils/           # 工具函数
│   ├── package.json
│   └── vite.config.ts
├── server/                   # Python 后端
│   ├── routers/             # FastAPI 路由
│   ├── services/            # 业务逻辑
│   │   ├── agent_service.py
│   │   ├── db_service.py
│   │   └── websocket_service.py
│   ├── tools/               # LangChain 工具
│   ├── models/              # 数据模型
│   ├── utils/               # 工具函数
│   ├── main.py              # 应用入口
│   ├── config.py            # 配置管理
│   └── requirements.txt
├── electron/                 # Electron 层（可选）
│   ├── main.js
│   └── preload.js
├── assets/                   # 生成的资产存储
├── .env.example             # 环境变量模板
└── README.md
```

#### 7.2 开发阶段规划

**阶段 1: 基础架构（1-2 周）**
- [ ] 前端项目搭建（React + TypeScript）
- [ ] 后端项目搭建（FastAPI）
- [ ] WebSocket 通信实现
- [ ] 数据库设计与实现
- [ ] 基础 UI 组件库

**阶段 2: Agent 系统（2-3 周）**
- [ ] LangGraph 多智能体架构
- [ ] 工具注册系统
- [ ] 流式响应处理
- [ ] 任务取消与管理
- [ ] 错误处理机制

**阶段 3: 核心功能（3-4 周）**
- [ ] 图像生成集成（至少 2 个模型）
- [ ] 视频生成集成（至少 1 个模型）
- [ ] 画布系统（可选）
- [ ] 聊天界面完善
- [ ] 资产管理功能

**阶段 4: 优化与测试（1-2 周）**
- [ ] 性能优化
- [ ] 错误处理完善
- [ ] 用户体验优化
- [ ] 单元测试与集成测试
- [ ] 文档编写

**阶段 5: 部署与发布（1 周）**
- [ ] Docker 容器化（Web 版）
- [ ] Electron 打包（桌面版）
- [ ] CI/CD 配置
- [ ] 部署文档

#### 7.3 开发最佳实践

**1. 环境变量管理**
```bash
# .env.example
# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1

# Replicate Configuration
REPLICATE_API_KEY=r8_...

# Application Settings
SERVER_PORT=8000
FRONTEND_PORT=5173
DATABASE_PATH=./data/app.db
ASSETS_PATH=./assets

# Development
DEBUG=true
LOG_LEVEL=INFO
```

**2. 日志系统**
```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name: str, log_file: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 文件处理器（带轮转）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 使用
logger = setup_logger('agent_service', 'logs/agent.log')
logger.info("Agent initialized")
```

**3. 错误监控**
```python
# 集成 Sentry（可选）
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

if not DEBUG:
    sentry_sdk.init(
        dsn="your-sentry-dsn",
        integrations=[FastApiIntegration()],
        traces_sample_rate=1.0,
    )
```

**4. API 测试**
```python
# tests/test_api.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_create_canvas():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/canvas", json={
            "title": "Test Canvas"
        })
        assert response.status_code == 200
        assert response.json()["title"] == "Test Canvas"
```

### 8. 关键技术要点总结

#### 8.1 前端核心要点

1. **状态管理分层**
   - IndexedDB 持久化 → TanStack Query
   - 服务端状态 → TanStack Query
   - 全局状态 → React Context
   - 局部状态 → Zustand

2. **实时通信模式**
   - HTTP POST 立即返回
   - WebSocket 推送流式结果
   - 支持任务取消

3. **性能优化**
   - 路由懒加载
   - 虚拟滚动
   - 消息批处理
   - 图像懒加载

#### 8.2 后端核心要点

1. **异步架构**
   - 所有 I/O 操作使用 `async/await`
   - FastAPI + Uvicorn (ASGI)
   - Socket.IO 异步模式

2. **Agent 系统**
   - LangGraph 状态图
   - 多智能体协作
   - 工具动态注册
   - 流式响应处理

3. **任务管理**
   - 后台任务创建
   - 任务取消支持
   - 进度实时推送
   - 异常处理与清理

#### 8.3 架构设计要点

1. **职责分离**
   ```
   Electron（可选） → 桌面应用壳
   React → UI 渲染与交互
   FastAPI → API 网关与业务逻辑
   LangGraph → Agent 编排
   Tools → 具体功能实现
   ```

2. **数据流向**
   ```
   用户输入 → React
   → HTTP POST → FastAPI
   → 创建后台任务 → LangGraph Agent
   → 调用工具 → 外部 AI API
   → WebSocket 推送 → React
   → UI 更新
   ```

3. **扩展性设计**
   - 工具插件化
   - Agent 可配置
   - 模型可切换
   - 存储可扩展

### 9. 常见问题与解决方案

#### Q1: WebSocket 连接不稳定？
**解决方案**：
```typescript
// 实现自动重连
const socketManager = new SocketIOManager({
  reconnection: true,
  reconnectionAttempts: 5,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000,
})
```

#### Q2: LLM 响应太慢？
**解决方案**：
1. 使用流式输出（SSE 或 WebSocket）
2. 前端显示"思考中"动画
3. 实现任务取消功能
4. 考虑使用更快的模型（如 GPT-4o-mini）

#### Q3: 图像生成失败如何处理？
**解决方案**：
```python
async def generate_image_with_retry(prompt: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return await call_image_api(prompt)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # 指数退避
```

#### Q4: 如何管理多个 API Key？
**解决方案**：
```python
class APIKeyRotator:
    def __init__(self, keys: List[str]):
        self.keys = keys
        self.current_index = 0
    
    def get_next_key(self) -> str:
        key = self.keys[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.keys)
        return key
```

#### Q5: 数据库查询性能问题？
**解决方案**：
```sql
-- 添加索引
CREATE INDEX idx_messages_session_id ON messages(session_id);
CREATE INDEX idx_assets_canvas_id ON assets(canvas_id);
CREATE INDEX idx_assets_created_at ON assets(created_at DESC);
```

---

## 总结

### Jaaz 项目的核心优势

1. **完整的技术栈**：覆盖前端、后端、桌面应用的全栈解决方案
2. **成熟的 Agent 架构**：基于 LangGraph 的多智能体系统
3. **丰富的模型集成**：支持主流图像/视频生成模型
4. **优秀的用户体验**：实时推送、任务取消、离线支持
5. **良好的扩展性**：工具插件化、Agent 可配置

### 构建视觉类 Agent 项目的关键路径

**最小可行产品（MVP）路线**：
1. **Week 1-2**: 基础架构
   - FastAPI + React 基础框架
   - WebSocket 实时通信
   - 简单的聊天界面

2. **Week 3-4**: Agent 系统
   - LangGraph 集成
   - 1 个图像生成工具
   - 流式响应实现

3. **Week 5-6**: 功能完善
   - 多模型支持
   - 资产管理
   - 配置界面

4. **Week 7-8**: 优化与部署
   - 性能优化
   - 错误处理
   - Docker 部署

### 推荐的学习资源

1. **LangGraph 官方文档**: https://langchain-ai.github.io/langgraph/
2. **FastAPI 官方文档**: https://fastapi.tiangolo.com/
3. **TanStack Query 文档**: https://tanstack.com/query/latest
4. **Socket.IO 文档**: https://socket.io/docs/
5. **Jaaz GitHub**: https://github.com/daemondw/jaaz

### 最后的建议

1. **从简单开始**：先实现核心功能，再逐步添加特性
2. **注重架构**：良好的架构设计会让后续开发更轻松
3. **充分测试**：AI 应用的不确定性要求更严格的测试
4. **用户反馈**：早期收集用户反馈，快速迭代
5. **性能监控**：从一开始就关注性能指标

通过深入学习 Jaaz 项目的架构设计，你可以快速构建出一个功能完整、性能优秀的视觉类 Agent 应用。祝你项目顺利！🚀

---

**文档版本**: v1.0  
**最后更新**: 2025-11-10  
**作者**: 基于 Jaaz 项目分析整理