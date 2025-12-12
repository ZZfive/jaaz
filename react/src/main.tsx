import { SocketProvider } from '@/contexts/socket' // websocket连接管理，用于实时通信
import { StrictMode } from 'react'
import ReactDOM from 'react-dom/client'  // ReactDOM，用于渲染React组件
import App from './App'  // 主应用组件
import { PostHogProvider } from 'posthog-js/react'  // PostHog，用于数据分析
import '@/assets/style/index.css'  // 样式文件

const options = {
  api_host: import.meta.env.VITE_PUBLIC_POSTHOG_HOST,
}

const rootElement = document.getElementById('root')!  // 获取根元素，找到index.html中的root元素；!表示非空断言，告诉TypeScript root元素一定存在
if (!rootElement.innerHTML) {  // 如果根元素不存在，则创建根元素
  const root = ReactDOM.createRoot(rootElement)  // 创建根元素
  root.render(
    <StrictMode>
      <PostHogProvider apiKey={import.meta.env.VITE_PUBLIC_POSTHOG_KEY} options={options}>
        <SocketProvider>
          <App />
        </SocketProvider>
      </PostHogProvider>
    </StrictMode>
  )
}
