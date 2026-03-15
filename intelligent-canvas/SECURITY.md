# 安全注意事项

## ⚠️ API Key 安全警告

当前项目在浏览器环境中直接使用 OpenAI API Key，这存在安全风险：

### 风险说明

1. **API Key 暴露**：浏览器中的代码可以被任何人查看，API Key 会暴露在客户端
2. **滥用风险**：恶意用户可能窃取你的 API Key 并滥用，导致费用损失
3. **配额耗尽**：API Key 可能被大量使用，耗尽你的配额

### 当前配置

项目已启用 `dangerouslyAllowBrowser: true`，**仅用于开发和演示目的**。

### 生产环境建议

#### 方案1：使用后端代理（推荐）

创建一个后端 API 来代理 OpenAI 请求：

```typescript
// 后端示例 (Node.js/Express)
app.post('/api/chat', async (req, res) => {
  const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY, // 从服务器环境变量读取
  })
  
  const completion = await openai.chat.completions.create({
    model: req.body.model,
    messages: req.body.messages,
  })
  
  res.json(completion)
})
```

前端调用：
```typescript
// 前端调用后端 API
const response = await fetch('/api/chat', {
  method: 'POST',
  body: JSON.stringify({ model, messages }),
})
```

#### 方案2：使用环境变量（仅限开发）

确保 `.env` 文件已添加到 `.gitignore`：

```bash
# .gitignore
.env
.env.local
.env.production
```

#### 方案3：使用 API Gateway

使用 AWS API Gateway、Cloudflare Workers 等服务作为代理层。

### 最佳实践

1. ✅ **开发环境**：可以使用 `dangerouslyAllowBrowser: true`，但使用测试 API Key
2. ✅ **生产环境**：必须使用后端代理，API Key 永远不要暴露在客户端
3. ✅ **API Key 管理**：
   - 使用环境变量存储
   - 定期轮换 API Key
   - 设置使用限额和监控
   - 使用不同的 Key 用于不同环境

### 当前项目的安全措施

- ✅ `.env` 文件已添加到 `.gitignore`
- ✅ `.env.example` 不包含真实 API Key
- ⚠️ 浏览器中直接使用 API Key（仅限开发）

### 如何迁移到后端代理

1. 创建后端服务（Node.js/Python/等）
2. 将 OpenAI API 调用移到后端
3. 前端通过 HTTP 请求调用后端 API
4. 后端验证请求并转发到 OpenAI
5. 移除前端的 `dangerouslyAllowBrowser` 选项

### 参考资源

- [OpenAI API 安全最佳实践](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety)
- [OpenAI API 文档](https://platform.openai.com/docs/api-reference)
