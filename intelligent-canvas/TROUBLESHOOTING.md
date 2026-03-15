# 页面空白问题排查指南

## 常见问题及解决方案

### 1. 检查浏览器控制台
打开浏览器开发者工具（F12），查看 Console 标签页是否有错误信息。

### 2. 检查网络请求
在 Network 标签页中，检查是否有资源加载失败（红色标记）。

### 3. 常见错误及解决方案

#### 错误：Cannot find module '@/xxx'
**原因**：路径别名 `@` 没有正确配置
**解决**：
1. 检查 `vite.config.ts` 中的 alias 配置
2. 检查 `tsconfig.json` 中的 paths 配置
3. 重启开发服务器

#### 错误：React Flow styles not found
**原因**：React Flow 样式文件未正确加载
**解决**：
```bash
npm install reactflow
# 确保导入样式
import 'reactflow/dist/style.css'
```

#### 错误：Module not found
**原因**：依赖未正确安装
**解决**：
```bash
rm -rf node_modules package-lock.json
npm install
```

### 4. 临时调试方法

如果页面完全空白，可以临时修改 `src/App.tsx`：

```tsx
import React from 'react'

function App() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>测试页面</h1>
      <p>如果你看到这个，说明基本渲染正常</p>
    </div>
  )
}

export default App
```

如果这个简单版本可以显示，说明问题在组件内部。

### 5. 检查文件结构

确保以下文件存在：
- ✅ `src/main.tsx`
- ✅ `src/App.tsx`
- ✅ `src/components/Canvas/IntelligentCanvas.tsx`
- ✅ `src/store/canvasStore.ts`
- ✅ `src/types/index.ts`

### 6. 检查环境变量

确保 `.env` 文件存在且格式正确：
```
VITE_OPENAI_API_KEY=your_key
VITE_OPENAI_BASE_URL=https://api.openai.com/v1
VITE_MODEL_NAME=gpt-4
```

### 7. 清除缓存

```bash
# 清除 Vite 缓存
rm -rf node_modules/.vite

# 清除浏览器缓存
# Chrome: Ctrl+Shift+Delete (Windows) 或 Cmd+Shift+Delete (Mac)
```

### 8. 检查端口占用

如果端口 3000 被占用，Vite 会自动使用其他端口。检查终端输出确认实际端口。

### 9. 查看终端错误

开发服务器的终端输出可能包含有用的错误信息。

## 如果以上都不行

1. 检查 `package.json` 中的依赖版本是否兼容
2. 尝试降级 React Flow 版本
3. 检查 Node.js 版本（推荐 v18+）
4. 查看完整的错误堆栈信息
