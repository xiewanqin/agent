# 如何查看错误信息

## ✅ 已修复所有错误！

所有 TypeScript 编译错误已修复，项目现在可以正常构建和运行了。

## 📋 查看错误的方法

### 方法1：使用终端/命令行（推荐）

在项目目录下运行构建命令：

```bash
cd /Users/xiewq/web/agent/intelligent-canvas
npm run build
```

这会显示所有 TypeScript 编译错误。如果构建成功，你会看到：
```
✓ built in X.XXs
```

### 方法2：查看开发服务器输出

启动开发服务器时，终端会显示实时错误：

```bash
npm run dev
```

如果有错误，会在终端中显示：
- ❌ 红色错误信息
- ⚠️ 黄色警告信息
- 📝 文件路径和行号

### 方法3：查看浏览器控制台（如果页面能打开）

1. 打开浏览器（Chrome/Firefox/Safari）
2. 按 `F12` 或 `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)
3. 查看 **Console** 标签页
4. 红色文字表示错误，黄色表示警告

### 方法4：查看日志文件

如果使用 yarn，错误日志会保存在：
```
yarn-error.log
```

## 🚀 现在可以启动项目了

```bash
# 1. 确保在项目目录
cd /Users/xiewq/web/agent/intelligent-canvas

# 2. 启动开发服务器
npm run dev

# 3. 浏览器会自动打开，或手动访问显示的地址（通常是 http://localhost:3000）
```

## 🔍 常见错误类型

### TypeScript 错误
- **格式**: `src/file.tsx(行号,列号): error TS错误码: 错误描述`
- **示例**: `src/App.tsx(5,10): error TS2322: Type 'string' is not assignable to type 'number'`
- **解决**: 查看指定文件和行号，修复类型问题

### 运行时错误
- **格式**: 在浏览器控制台显示
- **示例**: `Uncaught TypeError: Cannot read property 'xxx' of undefined`
- **解决**: 检查代码逻辑，添加空值检查

### 构建错误
- **格式**: 在 `npm run build` 时显示
- **示例**: `Module not found: Can't resolve '@/components/...'`
- **解决**: 检查文件路径和导入语句

## 📝 本次修复的错误

1. ✅ CustomNode 组件类型定义问题
2. ✅ React Flow Edge 类型兼容性问题
3. ✅ 未使用的导入和变量
4. ✅ Background variant 类型问题
5. ✅ Web Worker 空值检查问题
6. ✅ Connection 参数空值检查

## 💡 提示

- **开发时**: 使用 `npm run dev`，错误会实时显示
- **构建前**: 使用 `npm run build` 检查所有错误
- **生产环境**: 确保构建成功后再部署

现在项目应该可以正常运行了！🎉
