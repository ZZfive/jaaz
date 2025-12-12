import tailwindcss from '@tailwindcss/vite'  // CSS框架插件
import { TanStackRouterVite } from '@tanstack/router-plugin/vite'  // 路由插件，管理页面跳转
import react from '@vitejs/plugin-react'  // React插件，管理React组件
import path from 'path'  // Node.js的路径处理模块
import { defineConfig, UserConfig } from 'vite'  // Vite的配置模块

const PORT = 57988  // 后端服务端口号

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const isLibMode = mode === 'lib'  // 是否为库模式

  // Base configuration that applies to all environments
  const config: UserConfig = {
    plugins: [  // 插件配置
      !isLibMode &&  // 如果非库模式，则使用路由插件
      TanStackRouterVite({
        target: 'react',
        autoCodeSplitting: true,  // 自动代码分割
        generatedRouteTree: 'src/route-tree.gen.ts',  // 自动生成路由树文件
      }),
      react(),  // React插件
      tailwindcss(),  // CSS框架插件
    ].filter(Boolean),  // 过滤掉空值
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },  // 路径别名配置，用@符号代替src目录
    server: {  // 服务器配置
      port: 5174,
      proxy: {},
    },
  }

  // Library build configuration，库模式配置
  if (isLibMode) {
    config.build = {
      lib: {
        entry: path.resolve(__dirname, 'src/index.ts'),  // 库的入口文件
        name: '@jaaz/agent-ui',  // 库的名称
        fileName: (format: string) => `index.${format}.js`,  // 打包后的库的文件名
        formats: ['es'],  // 打包格式
      },
      rollupOptions: {
        external: [  // 外部依赖配置
          'react',
          'react-dom',
          'react/jsx-runtime',
          '@tanstack/react-router',
          '@tanstack/react-query',
          'i18next',
          'react-i18next',
          'framer-motion',
          'motion',
          'lucide-react',
          'sonner',
          'zustand',
          'immer',
          'nanoid',
          'ahooks',
          'socket.io-client',
          'openai',
          'clsx',
          'tailwind-merge',
          'class-variance-authority',
          /@radix-ui\/.*/,  // 正则表达式，匹配@radix-ui目录下的所有文件
          /@tanstack\/.*/,
          /@excalidraw\/.*/,
          /@mdxeditor\/.*/,
        ],
        output: {
          globals: {  // 全局变量配置
            react: 'React',
            'react-dom': 'ReactDOM',
            'react/jsx-runtime': 'react/jsx-runtime',
          },
        },
      },
    }
  }

  // Configure server based on environment，开发环境配置
  if (mode === 'development') {
    config.server = config.server || {}
    config.server.proxy = {
      '/api': {
        target: `http://127.0.0.1:${PORT}`,  // 访问 /api/xxx 时，会被转发到 http://127.0.0.1:57988/api/xxx
        changeOrigin: true,  // 修改请求头的origin，避免跨域问题
        // Uncomment the following if you want to remove the /api prefix when forwarding to Flask
        // rewrite: (path) => path.replace(/^\/api/, '')
      },
      // Also proxy WebSocket connections
      '/ws': {
        target: `ws://127.0.0.1:${PORT}`,
        ws: true,
      },
    }
  }

  return config
})
