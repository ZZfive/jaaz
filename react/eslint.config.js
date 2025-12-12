import js from '@eslint/js'  // 校验JS基础语法
import reactHooks from 'eslint-plugin-react-hooks'  // 校验React组件的hooks使用
import reactRefresh from 'eslint-plugin-react-refresh'  // 校验React热更新相关检查
import globals from 'globals'  // 校验全局变量使用
import tseslint from 'typescript-eslint'  // 校验TypeScript语法

export default tseslint.config(
  { ignores: ['dist'] },  // 忽略dist，即不检查dist目录
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],  // 继承JS基础语法和TypeScript基础语法
    files: ['**/*.{ts,tsx}'],  // 检查所有ts和tsx文件
    languageOptions: {
      ecmaVersion: 2020,  // 支持ES2020语法
      globals: globals.browser,  // 支持浏览器全局变量
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      '@typescript-eslint/no-unused-vars': 'off',  // 关闭未使用变量检查
      'react-refresh/only-export-components': [  // react热更新检查
        'warn',
        { allowConstantExport: true },
      ],
    },
  }
)
