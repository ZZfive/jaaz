import { ReactNode, Dispatch, SetStateAction } from 'react'

// Types
export interface Session {  // 会话类型
  id: string  // 会话ID
  title: string  // 会话标题
  created_at: string  // 会话创建时间
  updated_at: string  // 会话更新时间
  model: string  // 会话模型
  provider: string  // 模型提供商
}

export interface Message {
  role: 'user' | 'assistant' | 'system' | 'tool'
  content: string | any[]
  tool_calls?: any[]
  tool_call_id?: string
}

export interface Model {
  provider: string
  model: string
}

export interface ChatInterfaceProps { // 聊天界面组件属性
  canvasId: string  // 画布ID
  sessionList: Session[]  // 会话列表
  setSessionList: Dispatch<SetStateAction<Session[]>>  // 状态更新函数
  sessionId: string  // 当前会话ID
}

export interface ButtonProps {  // 按钮组件属性
  children: ReactNode  // 子组件
  variant?:  // 6种按钮样式变体
  | 'default'
  | 'destructive'
  | 'outline'
  | 'secondary'
  | 'ghost'
  | 'link'
  size?: 'default' | 'xs' | 'sm' | 'lg' | 'icon'  // 5种按钮尺寸选项
  className?: string  // 类名
  onClick?: () => void  // 点击事件
  disabled?: boolean  // 是否禁用
  asChild?: boolean  // 是否作为子组件
}

// Chat Components
export declare const ChatInterface: React.FC<ChatInterfaceProps>
export declare const ChatTextarea: React.FC<any>
export declare const ChatHistory: React.FC<any>
export declare const ChatMagicGenerator: React.FC<any>
export declare const ModelSelector: React.FC<any>
export declare const ModelSelectorV2: React.FC<any>
export declare const SessionSelector: React.FC<any>
export declare const ChatSpinner: React.FC<any>

// UI Components
export declare const Button: React.FC<ButtonProps>
export declare const Input: React.FC<any>
export declare const Avatar: React.FC<any>
export declare const AvatarImage: React.FC<any>
export declare const AvatarFallback: React.FC<any>
export declare const Badge: React.FC<any>
export declare const Card: React.FC<any>
export declare const CardHeader: React.FC<any>
export declare const CardFooter: React.FC<any>
export declare const CardTitle: React.FC<any>
export declare const CardAction: React.FC<any>
export declare const CardDescription: React.FC<any>
export declare const CardContent: React.FC<any>
export declare const Skeleton: React.FC<any>
export declare const ShinyText: React.FC<any>
export declare const ScrollArea: React.FC<any>
export declare const Separator: React.FC<any>
export declare const Switch: React.FC<any>
export declare const Tooltip: React.FC<any>
export declare const TooltipContent: React.FC<any>
export declare const TooltipProvider: React.FC<any>
export declare const TooltipTrigger: React.FC<any>

// Dialog Components
export declare const Dialog: React.FC<any>
export declare const DialogClose: React.FC<any>
export declare const DialogContent: React.FC<any>
export declare const DialogDescription: React.FC<any>
export declare const DialogFooter: React.FC<any>
export declare const DialogHeader: React.FC<any>
export declare const DialogOverlay: React.FC<any>
export declare const DialogPortal: React.FC<any>
export declare const DialogTitle: React.FC<any>
export declare const DialogTrigger: React.FC<any>

// Contexts & Hooks
export declare const AuthProvider: React.FC<{ children: ReactNode }>
export declare const useAuth: () => any
export declare const ConfigsProvider: React.FC<{ children: ReactNode }>
export declare const useConfigs: () => any
export declare const useDebounce: (callback: any, delay: number) => any
export declare const useTheme: () => any

// Utils
export declare const cn: (...classes: any[]) => string  // 类名合并工具
export declare const eventBus: any  // 事件总线
export declare const formatDate: (date: string | Date) => string  // 日期格式化工具
